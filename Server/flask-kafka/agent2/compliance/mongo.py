from pymongo import MongoClient

permission_map = {
    # Photo and Video
    "READ_MEDIA_IMAGES": "Photos and videos",
    "READ_MEDIA_VIDEO": "Photos and videos",
    "READ_MEDIA_VISUAL_USER_SELECTED": "Photos and videos",
    "ACCESS_MEDIA_LOCATION": "Photos and videos",
    "WRITE_EXTERNAL_STORAGE": "Photos and videos",
    "READ_EXTERNAL_STORAGE": "Photos and videos",

    # Audio
    "RECORD_AUDIO": "Audio",
    "MODIFY_AUDIO_SETTINGS": "Audio",

    # Contacts
    "READ_CONTACTS": "Contacts",
    "WRITE_CONTACTS": "Contacts",

    # Calendar
    "READ_CALENDAR": "Calendar",
    "WRITE_CALENDAR": "Calendar",

    # Location
    "ACCESS_FINE_LOCATION": "Location",
    "ACCESS_COARSE_LOCATION": "Location",
    "NEARBY_WIFI_DEVICES": "Location",

    # Personal Info
    "READ_PROFILE": "Personal info",
    "GET_ACCOUNTS": "Personal info",
    "AUTHENTICATE_ACCOUNTS": "Personal info",
    "MANAGE_ACCOUNTS": "Personal info",
    "USE_CREDENTIALS": "Personal info",

    # Financial Info
    "com.android.vending.BILLING": "Financial info",

    # Messages
    "READ_SMS": "Messages",
    "SEND_SMS": "Messages",
    "RECEIVE_SMS": "Messages",
    "READ_CALL_LOG": "Messages",
    "READ_PHONE_STATE": "Messages",
    "READ_PHONE_NUMBERS": "Messages",
    "ANSWER_PHONE_CALLS": "Messages",
    "CALL_PHONE": "Messages",

    # Device Id
    "com.google.android.gms.permission.AD_ID": "Device or other IDs",
    "ACCESS_ADSERVICES_AD_ID": "Device or other IDs",
    "ACCESS_ADSERVICES_ATTRIBUTION": "Device or other IDs",

    # App activity
    "GET_TASKS": "App activity",
    "REORDER_TASKS": "App activity",
    "RUN_USER_INITIATED_JOBS": "App activity",

    # App Info
    "BATTERY_STATS": "App info and performance",
    "FOREGROUND_SERVICE": "App info and performance",
    "FOREGROUND_SERVICE_CAMERA": "App info and performance",
    "FOREGROUND_SERVICE_MICROPHONE": "App info and performance",
    "FOREGROUND_SERVICE_MEDIA_PROJECTION": "App info and performance",
    "FOREGROUND_SERVICE_MEDIA_PLAYBACK": "App info and performance",
    "FOREGROUND_SERVICE_LOCATION": "App info and performance",
    "FOREGROUND_SERVICE_PHONE_CALL": "App info and performance",
    "FOREGROUND_SERVICE_CONNECTED_DEVICE": "App info and performance",
    "FOREGROUND_SERVICE_DATA_SYNC": "App info and performance",

    # Diagnostics
    "WAKE_LOCK": "Diagnostics",
    "VIBRATE": "Diagnostics",
    "ACCESS_NETWORK_STATE": "Diagnostics",
    "ACCESS_WIFI_STATE": "Diagnostics",
    "CHANGE_NETWORK_STATE": "Diagnostics",
    "CHANGE_WIFI_STATE": "Diagnostics",
    "INTERNET": "Diagnostics",

    # Notifications
    "POST_NOTIFICATIONS": "Notifications",

    # Security
    "USE_BIOMETRIC": "Security",
    "USE_FINGERPRINT": "Security",

    # Other
    "NFC": "Other",
    "SYSTEM_ALERT_WINDOW": "Other",
    "INSTALL_SHORTCUT": "Other",
    "UNINSTALL_SHORTCUT": "Other",
    "REQUEST_INSTALL_PACKAGES": "Other",
    "CREDENTIAL_MANAGER_SET_ALLOWED_PROVIDERS": "Other"
}


def minimize_permissions(raw_permissions):
    minimized = set()
    for perm in raw_permissions:
        if "Granted: true" in perm:
            for key, value in permission_map.items():
                if key in perm:
                    minimized.add(value)
    return list(minimized)


def get_app_data(device_id, package_name):
    client = MongoClient("mongodb://mongodb:27017/?replicaSet=rs0")
    db = client["app_data"]

    device = db.device_info.find_one({"deviceId": device_id})
    if not device:
        print(f"[!] No Device found with ID: {device_id}")
        return [], [], []

    apps = device.get("apps", [])
    app_entry = next((a for a in apps if a["packageName"] == package_name), None)
    granted_raw = app_entry.get("permissions", []) if app_entry else []
    granted = minimize_permissions(granted_raw)

    store_entry = db.playstore_info.find_one({"packageName": package_name})
    if not store_entry:
        print(f"[!] No Playstore Data found for the app: {package_name}")
        return granted, [], []

    data_collected = store_entry.get("dataCollected", [])
    data_shared = store_entry.get("dataShared", [])

    return granted, data_collected, data_shared

