import json
import logging
from datetime import datetime

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.exceptions import OpenSearchException
from settings import SETTINGS

logger = logging.getLogger("KafkaToOpenSearch")


def create_kafka_consumer() -> KafkaConsumer:
    """Create a new istance of Kafka Consumer.

    Raises:
        SystemExit: Kafka Consumer failed to initialize

    Returns:
        KafkaConsumer: Return new Kafka Consumer instance.
    """
    try:
        consumer: KafkaConsumer = KafkaConsumer(
            SETTINGS.kafka.topic,
            bootstrap_servers=SETTINGS.kafka.bootstrap_servers,
            group_id=SETTINGS.kafka.group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset=SETTINGS.kafka.starting_offsets,
            enable_auto_commit=SETTINGS.kafka.enable_auto_commit,
        )
        logger.info("KafkaConsumer initialized.")
        return consumer
    except KafkaError as e:
        logger.error(f"Failed to initialize KafkaConsumer: {e}")
        raise SystemExit(1)


def create_opensearch_client() -> OpenSearch:
    """Create an instance of OpenSearch client.

    Raises:
        SystemExit: _description_

    Returns:
        OpenSearch: Return new OpenSearch client instance.
    """
    try:
        client: OpenSearch = OpenSearch(
            hosts=[
                {"host": SETTINGS.opensearch.host, "port": SETTINGS.opensearch.port}
            ],
            http_auth=(SETTINGS.opensearch.username, SETTINGS.opensearch.password),
            use_ssl=SETTINGS.opensearch.use_ssl,
            verify_certs=SETTINGS.opensearch.verify_certs,
            connection_class=RequestsHttpConnection,
        )
        logger.info("OpenSearch client initialized.")
        return client
    except OpenSearchException as e:
        logger.error(f"Failed to connect to OpenSearch: {e}")
        raise SystemExit(1)


def get_opensearch_index_name(event_time_str: str) -> str:
    """Generate OpenSearch index name based on event time.

    Args:
        event_time_str (str): The event time string

    Returns:
        str: The generate index name.
    """
    dt = datetime.fromisoformat(event_time_str)
    return f"{SETTINGS.opensearch.index_prefix}-{dt.strftime('%Y_%m_%d')}"
