from pymongo import MongoClient
import json
import time
from pymongo.errors import PyMongoError
from mongo import get_app_data
from ollama_llm import ask_ollama, parse_response, build_llm_prompt
from kafka_out import send_compliance_result, build_kafka_message

MONGO_URI = "mongodb://mongodb:27017/?replicaSet=rs0"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["app_data"]
playstore_collection = db["playstore_info"]
device_collection = db["device_info"]


def process_entry(package_name):
    # Skip if already processed
    if playstore_collection.find_one({"packageName": package_name, "complianceChecked": True}):
        print(f"[Agent-2] Compliance already checked for {package_name}, skipping.")
        return

    # Mark immediately to prevent duplicate events
    playstore_collection.update_one(
        {"packageName": package_name},
        {"$set": {"complianceChecked": True}},
        upsert=True
    )

    # Process compliance for each device with the app
    devices = device_collection.find({"apps.packageName": package_name})
    for device in devices:
        device_id = device.get("deviceId")
        if not device_id:
            continue

        time.sleep(5)
        granted, collected, shared = get_app_data(device_id, package_name)

        prompt = build_llm_prompt(device_id, package_name, granted, collected, shared)
        response = ask_ollama(prompt)
        compliance, reason = parse_response(response)

        message = build_kafka_message(device_id, package_name, compliance, reason)

        if all(field in message for field in ("deviceId", "packageName", "compliance", "reason")):
            print("[Agent-2] Sending message to Kafka:")
            print(json.dumps(message, indent=2))
            send_compliance_result(message)
        else:
            print("[Agent-2] Invalid Kafka message, skipping:")
            print(message)


def run():
    print("Agent-2 listening on playstore_info...")
    try:
        with device_collection.watch(
            [{
                '$match': {
                    'operationType': 'update',
                    'updateDescription.updatedFields.installedApps': {'$exists': True}
                }
            }],
            full_document='updateLookup'
        ) as stream:
            for change in stream:
                full_doc = change.get('fullDocument', {})
                apps = full_doc.get('installedApps', [])
                if not apps:
                    continue

                new_app = apps[-1]
                print(f"New app detected: {new_app}")
                process_entry(new_app)

    except PyMongoError as e:
        print(f"MongoDB error: {e}")
    except KeyboardInterrupt:
        print("Interrupted manually.")


if __name__ == '__main__':
    run()

