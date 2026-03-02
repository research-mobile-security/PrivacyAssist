FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5100
CMD ["python", "consumer.py"]
