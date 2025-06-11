import os
from dataclasses import dataclass


@dataclass
class Settings:
    """
    Configuration settings for the IoT Stream Processor.

    These values are loaded from environment variables, providing sensible defaults
    where appropriate. Core Spark, Hadoop, and S3 configurations are expected
    to be passed directly to the Spark application via `spark-submit` arguments
    or through environment variables in the Docker Compose setup.
    """

    # --- General Application Settings -------------------------------------------
    LOGGING_LEVEL: str = os.environ.get("LOGGING_LEVEL", "INFO")
    """The logging level for the application (e.g., 'INFO', 'DEBUG', 'WARNING')."""

    # --- Apache Iceberg Table Identifiers ---------------------------------------
    ICEBERG_CATALOG: str = os.environ.get("ICEBERG_CATALOG", "spark_catalog")
    """
    The name of the Iceberg catalog to use (e.g., 'spark_catalog').
    This catalog itself must be configured externally in Spark properties.
    """
    ICEBERG_TABLE_IDENTIFIER: str = os.environ.get(
        "ICEBERG_TABLE_IDENTIFIER", "iot.events"
    )
    """The full identifier for the Iceberg table (e.g., 'catalog_name.database.table_name')."""

    # --- Kafka Settings ---------------------------------------------------------
    KAFKA_BOOTSTRAP_SERVERS: str = os.environ.get(
        "KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"
    )
    """Comma-separated list of Kafka broker addresses (e.g., 'kafka:9092,kafka2:9092')."""

    KAFKA_TOPIC: str = os.environ.get("KAFKA_TOPIC", "iot-events")
    """The Kafka topic to subscribe to for IoT events."""

    KAFKA_STARTING_OFFSETS: str = os.environ.get("KAFKA_STARTING_OFFSETS", "latest")
    """
    The starting offset for Kafka consumption ('latest' for new data,
    'earliest' for all historical data).
    """

    # --- Spark Structured Streaming Checkpoint & Trigger ------------------------
    CHECKPOINT_LOCATION: str = os.environ.get(
        "CHECKPOINT_LOCATION", "s3a://iot-data/checkpoints/events"
    )
    """
    The S3A/MinIO path where Spark Structured Streaming stores checkpoint metadata.
    Ensure this path is accessible by Spark and configured with proper credentials externally.
    """

    STREAMING_TRIGGER_INTERVAL: str = os.environ.get("STREAMING_TRIGGER_INTERVAL", None)
    """
    Optional: The interval for streaming micro-batch processing (e.g., '1 minute', '30 seconds').
    If not set (None), Spark processes batches as quickly as possible.
    """

    # --- Iceberg Table Properties (Applied during table creation/alteration) ----
    ICEBERG_WRITE_FORMAT_DEFAULT: str = os.environ.get(
        "ICEBERG_WRITE_FORMAT_DEFAULT", "parquet"
    )
    """The default file format for new data files written to the Iceberg table ('parquet' or 'orc')."""

    ICEBERG_FORMAT_VERSION: str = os.environ.get("ICEBERG_FORMAT_VERSION", "2")
    """The Iceberg table format version ('1' or '2'). Version 2 enables features like row-level deletes."""

    ICEBERG_HISTORY_EXPIRE_MAX_SNAPSHOTS: str = os.environ.get(
        "ICEBERG_HISTORY_EXPIRE_MAX_SNAPSHOTS", "10"
    )
    """The maximum number of historical snapshots to retain for table rollback."""

    ICEBERG_HISTORY_EXPIRE_MIN_SNAPSHOTS_TO_RETAIN: str = os.environ.get(
        "ICEBERG_HISTORY_EXPIRE_MIN_SNAPSHOTS_TO_RETAIN", "1"
    )
    """The minimum number of historical snapshots to always keep, even if they exceed max_snapshots."""

    ICEBERG_WRITE_DATA_TARGET_FILE_SIZE_BYTES: str = os.environ.get(
        "ICEBERG_WRITE_DATA_TARGET_FILE_SIZE_BYTES", "536870912"
    )
    """
    The target size for data files written to the Iceberg table, in bytes
    (e.g., 536870912 bytes = 512 MB). Influences file count and read performance.
    """
    ICEBERG_WRITE_PARQUET_COMPRESSION_CODEC: str = os.environ.get(
        "ICEBERG_WRITE_PARQUET_COMPRESSION_CODEC", "zstd"
    )
    """The compression codec for Parquet files ('snappy', 'gzip', 'zstd', 'lz4')."""

    ICEBERG_OPTIMIZE_REWRITE_DATA_ENABLED: str = os.environ.get(
        "ICEBERG_OPTIMIZE_REWRITE_DATA_ENABLED", "false"
    )
    """
    Whether to enable default data file rewriting (compaction) for optimization.
    Set to 'true' to allow Iceberg's optimize actions.
    """
    ICEBERG_OPTIMIZE_REWRITE_DATA_TARGET_FILE_SIZE_BYTES: str = os.environ.get(
        "ICEBERG_OPTIMIZE_REWRITE_DATA_TARGET_FILE_SIZE_BYTES", "1073741824"
    )
    """
    The target file size for optimization operations, in bytes
    (e.g., 1073741824 bytes = 1 GB). Used when consolidating smaller files.
    """


# Create a single shared config instance to be imported throughout the application
SETTINGS = Settings()
