import json
import logging
import random
import signal
import time
from datetime import datetime, timezone

from kafka import KafkaProducer
from kafka.errors import KafkaError
from settings import SETTINGS

# Logging setup
logging.basicConfig(
    level=SETTINGS.logging_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("IoTDataSimulator")

running = True


def handle_shutdown(signum, frame):
    global running
    logger.info(f"Received shutdown signal ({signum}). Stopping simulation...")
    running = False


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


def create_kafka_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=SETTINGS.kafka.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        logger.info("KafkaProducer initialized.")
        return producer
    except KafkaError as e:
        logger.error(f"Failed to initialize KafkaProducer: {e}")
        raise SystemExit(1)


def generate_iot_data():
    data = {
        "device_id": random.choice(SETTINGS.simulation.device_ids),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    for var, (vmin, vmax) in SETTINGS.simulation.variable_ranges.items():
        data[var] = round(random.uniform(vmin, vmax), 2)

    return data


def run_simulation():
    logger.info("Starting IoT data simulation...")

    producer = create_kafka_producer()

    try:
        while running:
            data = generate_iot_data()
            try:
                producer.send(SETTINGS.kafka.topic, value=data)
                logger.info(f"Sent data: {data}")
            except KafkaError as e:
                logger.error(f"Failed to send data to Kafka: {e}")
            time.sleep(SETTINGS.simulation.sleep_interval_seconds)
    except Exception as e:
        logger.exception(f"Unexpected error in data simulator: {e}")
    finally:
        producer.close()
        logger.info("Kafka producer closed.")


if __name__ == "__main__":
    run_simulation()
