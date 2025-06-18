import logging
import signal

from kafka import KafkaConsumer
from opensearchpy import OpenSearch
from opensearchpy.exceptions import OpenSearchException
from settings import SETTINGS
from utils import (
    create_kafka_consumer,
    create_opensearch_client,
    get_opensearch_index_name,
)

# Logging setup
logging.basicConfig(
    level=SETTINGS.logging_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("KafkaToOpenSearch")

running = True


def handle_shutdown(signum, frame):
    global running
    logger.info(f"Received shutdown signal ({signum}). Shutting down consumer...")
    running = False


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


def run_consumer():
    logger.info("Starting Kafka to OpenSearch pipeline...")

    consumer: KafkaConsumer = create_kafka_consumer()
    opensearch: OpenSearch = create_opensearch_client()

    try:
        while running:
            for message in consumer:
                try:
                    doc = message.value

                    # Minimal schema validation
                    required_fields = {"device_id", "event_time", "variable_id"}
                    if not required_fields.issubset(doc):
                        logger.warning(f"Incomplete document received, skipping: {doc}")
                        continue

                    index_name = get_opensearch_index_name(doc["event_time"])

                    response = opensearch.index(
                        index=index_name,
                        document=doc,
                    )
                    logger.info(f"Indexed document to {index_name}: {response['_id']}")
                except OpenSearchException as e:
                    logger.error(f"Failed to index document in OpenSearch: {e}")
                except Exception as e:
                    logger.exception(f"Unexpected error processing message: {e}")

                if not running:
                    break

    except Exception as e:
        logger.exception(f"Unexpected error in Kafka consumer: {e}")
    finally:
        consumer.close()
        logger.info("Kafka consumer closed.")


if __name__ == "__main__":
    run_consumer()
