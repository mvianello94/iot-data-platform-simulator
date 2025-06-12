import logging

from pyspark.sql import SparkSession
from settings import SETTINGS  # import del singleton con i nuovi settings

logger = logging.getLogger("IoTStreamProcessorUtils")


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
        raise


def create_iot_events_iceberg_table(spark: SparkSession, table_identifier: str) -> None:
    """
    Creates an Apache Iceberg table for IoT events if it does not already exist.
    Raises exception if creation/verifying fails.

    Args:
        spark (SparkSession): active Spark session.
        table_identifier (str): full iceberg table identifier.

    """
    logger.info(f"Checking/creating Iceberg table '{table_identifier}'...")

    try:
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {table_identifier} (
                device_id STRING,
                event_time TIMESTAMP,
                variable_id STRING,
                string_val STRING,
                double_val DOUBLE,
                year INT,
                month INT,
                day INT
            )
            USING iceberg
            PARTITIONED BY (year, month, day)
            TBLPROPERTIES (
                'write.format.default'='{SETTINGS.iceberg.write_format_default}',
                'format-version'='{SETTINGS.iceberg.format_version}',
                'history.expire.max-snapshots'='{SETTINGS.iceberg.history_expire_max_snapshots}',
                'history.expire.min-snapshots-to-retain'='{SETTINGS.iceberg.history_expire_min_snapshots_to_retain}',
                'write.data.target-file-size-bytes'='{SETTINGS.iceberg.write_data_target_file_size_bytes}',
                'write.parquet.compression-codec'='{SETTINGS.iceberg.write_parquet_compression_codec}',
                'optimize.rewrite-data.enabled'='{str(SETTINGS.iceberg.optimize_rewrite_data_enabled).lower()}',
                'optimize.rewrite-data.target-file-size-bytes'='{SETTINGS.iceberg.optimize_rewrite_data_target_file_size_bytes}',
                'checkpoint_location'='{SETTINGS.spark_streaming.checkpoint_location}'
            )
        """)
        logger.info(f"Iceberg table '{table_identifier}' ensured to exist.")
    except Exception as e:
        logger.error(
            f"Failed to create or verify Iceberg table '{table_identifier}': {e}",
            exc_info=True,
        )
        raise
