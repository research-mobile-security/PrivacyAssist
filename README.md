# 📱 Privacy Compliance Service

This project aims to monitor the **privacy compliance of Android apps** by comparing the permissions actually granted on the device with the data declared in the "Data Safety" section of the Google Play Store. It uses a **microservices architecture** based on Kafka, MongoDB, and Flask, and is designed to run in a Docker environment.

## ⚙️ Project Architecture

<img src="https://github.com/research-mobile-security/privacyassist/blob/main/project-image/figure-architecture4.png">

The architecture consists of two main agents:

### Agent-1 (Smartphone)
- Collects:
  - **Package name** of installed apps
  - **Granted permissions** for each app
  - **Device ID**
- Sends the data via **Kafka** to the server
- Receives the **compliance result** and shows an **alert** to the user

### Agent-2 (Server)
1. **Kafka Consumer**:
   - Receives data from Agent-1
   - Stores package name, permissions, and ID in MongoDB
2. **MongoDB**:
   - Database used to store information from both the Kafka consumer and the Data Safety Scraper
   - Divided into two collections:
     - **device_info** (device info, installed apps with their permissions)
     - **playstore_info** (package names with associated Data Safety data)

3. **Data Safety Scraper**:
   - Extracts the *Data Safety* section (Data Collected & Data Shared) for each app from the Google Play Store
   - Saves the collected data into MongoDB

4. **Privacy Compliance Checker**:
   - Compares granted permissions (from the Smartphone) with those declared on the Play Store
   - Evaluates compliance using a local LLM (Ollama)
   - Sends the results to Kafka to notify Agent-1

---

## 🗂️ Folder Structure

```
Server/
├── scraping/
│   └── webScraper.py              # Scrapes Data Collected and Data Shared from Play Store.
└── flask-kafka/
    ├── docker-compose.yml
    ├── init-mongo/
    │   └── init.js
    ├── agent1/
    │   ├── producer/
    │   │   ├── Dockerfile
    │   │   ├── requirements.txt
    │   │   └── server.py           # Flask server to receive data from Android
    │   └── consumer/
    │       ├── Dockerfile
    │       ├── requirements.txt
    │       └── consumer.py         # Receives compliance result and triggers alert
    ├── agent2/
    │   ├── consumer/
    │   │   ├── Dockerfile
    │   │   ├── requirements.txt
    │   │   └── kafka_to_mongodb.py # Consumes data from Kafka and saves to MongoDB
    │   └── compliance/
    │       ├── Dockerfile
    │       ├── requirements.txt
    │       ├── agent2_compliance.py # Compares permissions and data safety
    │       ├── mongo.py             # DB access logic
    │       ├── ollama_llm.py        # LLM model invocation
    │       └── kafka_out.py         # Kafka producer with compliance result
    └── start-ollama.sh
```

---

## ⚠️ Requirements

- Python 3.10+
- Docker and Docker Compose
- ChromeDriver (same version as your installed Chrome browser)
- Kafka
- MongoDB
- Ollama (optional, for local LLM)
- Tested on Linux environments

---

## 🚀 Getting Started

### 1. Clone the project

```bash
git clone <repo-url>
cd Server/flask-kafka
```

### 2. Start the services

```bash
docker-compose up --build
```

### 3. Start Ollama (if used for compliance checking)

```bash
./start-ollama.sh
```

### 4. Run the webScraper (keep it running during interactions)

```bash
cd ..
cd scraping
python3 webScraper
```


