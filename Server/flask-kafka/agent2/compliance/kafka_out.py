import os
import json
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

producer = None
while producer is None:
    try:
        producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
            value_serializer=lambda m: json.dumps(m).encode("utf-8")
        )
        print(" Kafka connection established successfully")
    except NoBrokersAvailable:
        print(" Kafka service is not reachable")
        time.sleep(5)

def build_kafka_message(device_id, package_name, compliance, reason):
    return {
        "deviceId": device_id,
        "packageName": package_name,
        "compliance": compliance,
        "reason": reason,
    }

def send_compliance_result(message):
    topic= "privacy-compliance"
    producer.send(topic, message)
    producer.flush()
    print(f" Compliance result sent to topic: {topic}")

