import json
import threading
import time
from flask import Flask, jsonify
from kafka import KafkaConsumer

app = Flask(__name__)
alerts = {}

def kafka_listener():
    consumer = KafkaConsumer(
        'privacy-compliance',
        bootstrap_servers='kafka:9092',
        group_id='flask-alert-group',
        auto_offset_reset='earliest',  # listen  messages
        enable_auto_commit=False,
        value_deserializer=lambda m: m  # Receive raw message
    )

    consumer.subscribe(['privacy-compliance'])

    print('[Kafka] Waiting for topic partition assignment...')
    while not consumer.assignment():
        print("[Kafka DEBUG] Waiting for topic partition assignment...")
        consumer.poll(timeout_ms=100)

    print(f"[Kafka DEBUG] Assigned partitions: {consumer.assignment()}")
    print("[Kafka] Listening for new messages on 'privacy-compliance'...")

    while True:
        raw_messages = consumer.poll(timeout_ms=1000)
        if not raw_messages:
            continue

        for tp, messages in raw_messages.items():
            for msg in messages:
                print(f"[Kafka]  Raw message: {msg.value}")
                try:
                    text = msg.value.decode('utf-8').strip()
                    print(f"[Kafka] 🔸 Decoded: {text}")
                    if not text:
                        print("[Kafka]  Empty message, skipped.")
                        continue

                    data = json.loads(text)
                    device_id = data.get('deviceId')
                    if not device_id:
                        print('[Kafka WARNING] No deviceId, skipping.')
                        continue

                    alerts[device_id] = data
                    print(f"[Kafka]  Alert stored for {device_id}")
                except Exception as e:
                    print(f"[Kafka ERROR] Invalid JSON message: {e}")
                finally:
                    consumer.commit()

# Endpoint GET for Android
@app.route('/alert-compliance/<device_id>', methods=['GET'])
def get_alert(device_id):
    if device_id in alerts:
        print(f"[Flask] Returning alert for device {device_id}")
        return jsonify(alerts[device_id]), 200
    else:
        print(f"[Flask] No alert found for device {device_id}")
        return jsonify({"message": "No compliance alert found for this device"}), 404

if __name__ == '__main__':
    threading.Thread(target=kafka_listener, daemon=True).start()
    time.sleep(2)
    print("[Main] Flask starting on port 5100")
    app.run(host='0.0.0.0', port=5100)

