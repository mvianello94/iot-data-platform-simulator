import logging

from pyspark.sql import SparkSession

# No longer importing pyspark.sql.types if we're not using them for explicit schema definition
# from pyspark.sql.types import StructType, StringType, DoubleType, TimestampType, IntegerType
from settings import SETTINGS  # Assuming SETTINGS is well-defined

logger = logging.getLogger("IoTStreamProcessorUtils")  # Use a specific logger for utils


def get_spark_session() -> SparkSession:
    """
    Initializes and returns a SparkSession.
    Assumes core Spark configurations (like S3/MinIO, Iceberg catalog setup)
    are passed externally via spark-submit arguments or Docker Compose environment variables.
    """
    logger.info("Attempting to create SparkSession...")

    try:
        spark_builder = SparkSession.builder.appName("IoTStreamProcessor")
        spark: SparkSession = spark_builder.getOrCreate()
        logger.info("SparkSession created successfully.")
        return spark
    except Exception as e:
        logger.error(f"Failed to create SparkSession: {e}", exc_info=True)
        raise  # Re-raise the exception to be handled by the caller


def create_iot_events_iceberg_table(spark: SparkSession, table_identifier: str) -> None:
    """
    Creates an Apache Iceberg table for IoT events if it does not already exist.
    If the table cannot be created or verified, an exception is raised.

    Args:
        spark (SparkSession): The active SparkSession.
        table_identifier (str): The full identifier of the Iceberg table (e.g., "catalog.database.table").

    Raises:
        Exception: If the table creation or verification process fails.
    """
    logger.info(f"Checking/creating Iceberg table '{table_identifier}'...")

    try:
        # Using SQL DDL to create the table
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {table_identifier} (
                device_id STRING,
                temperature DOUBLE,
                humidity DOUBLE,
                event_time TIMESTAMP,
                year INT,
                month INT,
                day INT
            )
            USING iceberg
            PARTITIONED BY (year, month, day)
            TBLPROPERTIES (
                'write.format.default'='{SETTINGS.ICEBERG_WRITE_FORMAT_DEFAULT}',
                'format-version'='{SETTINGS.ICEBERG_FORMAT_VERSION}',
                'history.expire.max-snapshots'='{SETTINGS.ICEBERG_HISTORY_EXPIRE_MAX_SNAPSHOTS}',
                'history.expire.min-snapshots-to-retain'='{SETTINGS.ICEBERG_HISTORY_EXPIRE_MIN_SNAPSHOTS_TO_RETAIN}',
                'write.data.target-file-size-bytes'='{SETTINGS.ICEBERG_WRITE_DATA_TARGET_FILE_SIZE_BYTES}',
                'write.parquet.compression-codec'='{SETTINGS.ICEBERG_WRITE_PARQUET_COMPRESSION_CODEC}',
                'optimize.rewrite-data.enabled'='{SETTINGS.ICEBERG_OPTIMIZE_REWRITE_DATA_ENABLED}',
                'optimize.rewrite-data.target-file-size-bytes'='{SETTINGS.ICEBERG_OPTIMIZE_REWRITE_DATA_TARGET_FILE_SIZE_BYTES}',
                'checkpoint_location'='{SETTINGS.CHECKPOINT_LOCATION}'
            )
        """)
        logger.info(f"Iceberg table '{table_identifier}' ensured to exist.")
    except Exception as e:
        logger.error(
            f"Failed to create or verify Iceberg table '{table_identifier}': {e}",
            exc_info=True,
        )
        # Re-raise the exception after logging, to be caught by the main application flow
        raise
