import os
import json
import time
import threading
from kafka import KafkaConsumer
from pymongo import MongoClient
from kafka.errors import NoBrokersAvailable

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/?replicaSet=rs0")

def start_consumer():
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["app_data"]
    device_collection = db["device_info"]

    consumer = None
    while consumer is None:
        try:
            consumer = KafkaConsumer(
                "device-info",
                bootstrap_servers=KAFKA_BOOTSTRAP,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="mongo-writer"
            )
            print(" Connected to Kafka")
        except NoBrokersAvailable:
            print(" Kafka is currently unavailable")
            time.sleep(5)

    print(" Listen on  Kafka...")
    for message in consumer:
        data = message.value
        device_id = data.get("androidId")
        device_name = data.get("deviceName")
        mac_address = data.get("macAddress")
        app_id = data.get("packageName")
        permissions = data.get("grantedPermissions", [])

        if not (device_id and app_id):
            continue

        # First update : Update basic info and remove any duplicate from app
        device_collection.update_one(
            {"deviceId": device_id},
            {
                "$set": {
                    "deviceName": device_name,
                    "macAddress": mac_address
                },
                "$pull": {
                    "apps": {"packageName": app_id}
                }
            }
        )

        # Second update: Add app to installedApps and apps[] with permissions
        device_collection.update_one(
            {"deviceId": device_id},
            {
                "$addToSet": {
                    "installedApps": app_id,
                    "apps": {
                        "packageName": app_id,
                        "permissions": permissions
                    }
                }
            },
            upsert=True
        )

        print(f" Saved: {device_id} → {app_id}")

if __name__ == "__main__":
    print(" Start consumer Agent-2...")
    threading.Thread(target=start_consumer).start()


