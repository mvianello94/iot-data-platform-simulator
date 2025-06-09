import json
import logging
import random
import time
from datetime import datetime

from config import CONFIG
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Configure logging
logger = logging.getLogger("IoTDataSimulator")
logger.setLevel(CONFIG.LOGGING_LEVEL)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

try:
    producer = KafkaProducer(
        bootstrap_servers="kafka:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    logger.info("KafkaProducer initialized.")
except KafkaError as e:
    logger.error(f"Failed to initialize KafkaProducer: {e}")
    raise SystemExit(1)

device_ids = ["sensor-1", "sensor-2", "sensor-3"]

logger.info("Starting IoT data simulation...")
try:
    while True:
        data = {
            "device_id": random.choice(device_ids),
            "temperature": round(random.uniform(20.0, 30.0), 2),
            "humidity": round(random.uniform(30.0, 70.0), 2),
            "timestamp": datetime.utcnow().isoformat(),
        }
        try:
            producer.send("iot-events", value=data)
            logger.info(f"Sent data: {data}")
        except KafkaError as e:
            logger.error(f"Failed to send data to Kafka: {e}")
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Simulation interrupted by user.")
except Exception as e:
    logger.exception(f"Unexpected error in data simulator: {e}")
finally:
    producer.close()
    logger.info("Kafka producer closed.")
