import json
import threading
from flask import Flask, request, jsonify
from kafka import KafkaProducer

app = Flask(__name__)

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_to_kafka_async(topic, data):
    try:
        producer.send(topic, data)
        producer.flush()
        print(f"[Kafka] Sent to topic '{topic}': {data}")
    except Exception as e:
        print(f"[Kafka ❌ ERROR] {e}")

@app.route('/send', methods=['POST'])
def send():
    data = request.json
    print(f"[Flask]  Received from Android: {data}")
    threading.Thread(target=send_to_kafka_async, args=("device-info", data), daemon=True).start()
    return jsonify({"status": "ok", "data": data}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

