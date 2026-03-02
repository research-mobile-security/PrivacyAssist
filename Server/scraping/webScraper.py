
import os
import time
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Start Chrome WebDriver
try:
    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("Chrome WebDriver started successfully")
except Exception as e:
    print(f"Failed to start Chrome WebDriver: {e}")
    raise SystemExit(1)

# Connect to MongoDB
mongo_client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongodb:27017/"))
db = mongo_client["app_data"]
device_collection = db["device_info"]
playstore_collection = db["playstore_info"]

def extract_data_safety(app_id):
    try:
        url = f"https://play.google.com/store/apps/datasafety?id={app_id}&hl=en"
        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.XgPdwe"))
        )
        time.sleep(3)

        data_shared_array = []
        data_collected_array = []

        div_lists = driver.find_elements(By.CSS_SELECTOR, "div.XgPdwe")

        try:
            h3_elements = div_lists[0].find_elements(By.CSS_SELECTOR, "h3.aFEzEb")
            for h3 in h3_elements:
                data_shared_array.append(h3.text.strip())
        except Exception as e:
            print(f"Error parsing shared data block: {e}")

        try:
            h3_elements = div_lists[1].find_elements(By.CSS_SELECTOR, "h3.aFEzEb")
            for h3 in h3_elements:
                data_collected_array.append(h3.text.strip())
        except Exception as e:
            print(f"Error parsing collected data block: {e}")

        return {
            "packageName": app_id,
            "dataShared": data_shared_array,
            "dataCollected": data_collected_array
        }

    except Exception as e:
        print(f"Error scraping {app_id}: {e}")
        return None

# Start listening to MongoDB updates
print("Listening for updates in MongoDB...")
try:
    with device_collection.watch([
    {
        '$match': {
            'operationType': 'update',
            'updateDescription.updatedFields.installedApps': {'$exists': True}
        }
    }
], full_document='updateLookup') as stream:

        for change in stream:
            full_doc = change["fullDocument"]
            apps = full_doc.get("installedApps", [])
            if not apps:
                continue

            new_app = apps[-1]
            print(f"New app detected: {new_app}")

            if playstore_collection.find_one({"packageName": new_app}):
                print(f"App already scraped: {new_app}")
                continue

            safety_info = extract_data_safety(new_app)
            if safety_info:
                playstore_collection.update_one(
                    {"packageName": new_app},
                    {"$set": safety_info},
                    upsert=True
                )
                print(f"Data saved for: {new_app}")

except PyMongoError as e:
    print(f"MongoDB error: {e}")
except KeyboardInterrupt:
    print("Interrupted manually")

# Cleanup
print("Done. Closing browser.")
driver.quit()

