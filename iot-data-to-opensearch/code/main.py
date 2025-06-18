import logging
import signal
import time

from kafka import KafkaConsumer
from opensearchpy import OpenSearch, helpers
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

    batch = []
    last_flush = time.time()

    try:
        while running:
            msg_pack = consumer.poll(timeout_ms=500, max_records=50)
            for tp, messages in msg_pack.items():
                for message in messages:
                    doc = message.value

                    # Minimal schema validation
                    required_fields = {"device_id", "event_time", "variable_id"}
                    if not required_fields.issubset(doc):
                        logger.warning(f"Incomplete document received, skipping: {doc}")
                        continue

                    index_name = get_opensearch_index_name(doc["event_time"])
                    action = {
                        "_index": index_name,
                        "_source": doc,
                    }
                    batch.append(action)

            # Flush if batch is big enough or time passed
            if (
                len(batch) >= SETTINGS.opensearch.max_batch_size
                or (time.time() - last_flush)
                >= SETTINGS.opensearch.flush_interval_seconds
            ):
                if batch:
                    try:
                        success, errors = helpers.bulk(opensearch, batch)
                        logger.info(f"Bulk indexed {success} documents to OpenSearch.")
                        if errors:
                            logger.warning(
                                f"Some errors occurred during bulk indexing: {errors}"
                            )
                    except OpenSearchException as e:
                        logger.error(f"Bulk indexing failed: {e}")
                    finally:
                        batch.clear()
                        last_flush = time.time()

    except Exception as e:
        logger.exception(f"Unexpected error in Kafka consumer: {e}")
    finally:
        if batch:
            logger.info("Flushing remaining documents before shutdown...")
            try:
                helpers.bulk(opensearch, batch)
                logger.info(f"Final bulk flush of {len(batch)} documents complete.")
            except Exception as e:
                logger.error(f"Final flush failed: {e}")
        consumer.close()
        logger.info("Kafka consumer closed.")


if __name__ == "__main__":
    run_consumer()
