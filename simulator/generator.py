import json
import random
import time
from datetime import datetime

from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

device_ids = ["sensor-1", "sensor-2", "sensor-3"]

while True:
    data = {
        "device_id": random.choice(device_ids),
        "temperature": round(random.uniform(20.0, 30.0), 2),
        "humidity": round(random.uniform(30.0, 70.0), 2),
        "timestamp": datetime.utcnow().isoformat(),
    }
    producer.send("iot-events", value=data)
    print("Sent:", data)
    time.sleep(1)
