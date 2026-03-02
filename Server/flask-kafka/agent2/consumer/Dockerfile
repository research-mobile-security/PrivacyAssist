FROM python:3.11-slim

WORKDIR /app

COPY . /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Run the Kafka → MongoDB ingestion script
CMD ["python", "kafka_to_mongodb.py"]
