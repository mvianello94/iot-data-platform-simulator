import logging

from listener import StreamingListener
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    dayofmonth,
    explode,
    from_json,
    month,
    to_timestamp,
    when,
    year,
)
from pyspark.sql.types import StringType, StructType
from settings import SETTINGS
from utils import create_iot_telemetry_iceberg_table, get_spark_session

# Configure logging
logging.basicConfig(
    level=SETTINGS.logging_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("IoTStreamProcessor")

# Minimal schema just to extract device_id and timestamp
BASE_SCHEMA = (
    StructType()
    .add("device_id", StringType(), nullable=False)
    .add("timestamp", StringType(), nullable=False)
)


def main() -> None:
    """
    Main function to run the IoT Stream Processor application.
    Reads IoT telemetry from Kafka, normalizes them, and writes to an Iceberg table.
    """
    logger.info("Starting IoT Stream Processor application...")

    spark: SparkSession = None
    try:
        spark = get_spark_session()
        spark.streams.addListener(StreamingListener())
        logger.info("Spark session created and listener attached.")
    except Exception as e:
        logger.critical(f"Failed to create Spark session: {e}", exc_info=True)
        exit(1)

    try:
        create_iot_telemetry_iceberg_table(
            spark=spark,
            table_identifier=f"{SETTINGS.iceberg.catalog}.{SETTINGS.iceberg.table_identifier}",
        )
        logger.info("Iceberg table check/creation complete.")
    except Exception as e:
        logger.critical(f"Failed to create/verify Iceberg table: {e}", exc_info=True)
        if spark:
            spark.stop()
        exit(1)

    df: DataFrame
    try:
        df = (
            spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", SETTINGS.kafka.bootstrap_servers)
            .option("subscribe", SETTINGS.kafka.topic)
            .option("startingOffsets", SETTINGS.kafka.starting_offsets)
            .load()
        )
        logger.info("Kafka stream reader initialized.")
    except Exception as e:
        logger.critical(f"Failed to initialize Kafka stream reader: {e}", exc_info=True)
        if spark:
            spark.stop()
        exit(1)

    logger.debug("Parsing JSON payload and normalizing IoT event data...")

    # Step 1: Parse fixed fields (device_id, timestamp) and keep original JSON string.
    parsed_df: DataFrame = (
        df.selectExpr("CAST(value AS STRING) as json")
        .select(from_json(col("json"), BASE_SCHEMA).alias("meta"), "json")
        .select("meta.device_id", "meta.timestamp", "json")
    )

    # Step 2: Convert full JSON string into map<string,string> for dynamic keys, then normalize.
    # The 'explode' function transforms map entries into new rows.
    normalized_df: DataFrame = (
        parsed_df.withColumn("event_time", to_timestamp("timestamp"))
        .drop("timestamp")  # Drop the original string timestamp column
        .withColumn("json_map", from_json(col("json"), "map<string,string>"))
        # IMPORTANT FIX: Use select and provide two aliases for explode's output
        .select(
            "device_id",
            "event_time",
            explode(col("json_map")).alias("variable_key", "variable_value"),
        )
        .filter(
            ~col("variable_key").isin("device_id", "timestamp")
        )  # Exclude already extracted base fields
        .select(
            "device_id",
            "event_time",
            col("variable_key").alias("variable_id"),
            col("variable_value").alias("string_val"),
            # Attempt to cast value to double; null if not convertible
            when(
                col("variable_value").cast("double").isNotNull(),
                col("variable_value").cast("double"),
            ).alias("double_val"),
            year("event_time").alias("year"),
            month("event_time").alias("month"),
            dayofmonth("event_time").alias("day"),
        )
    )

    logger.debug("Data normalization complete. Starting write to Iceberg...")

    try:
        query_writer = (
            normalized_df.writeStream.format("iceberg")
            .outputMode("append")
            .option("checkpointLocation", SETTINGS.spark_streaming.checkpoint_location)
        )

        if SETTINGS.spark_streaming.trigger_interval:
            logger.info(
                f"Setting streaming trigger interval to {SETTINGS.spark_streaming.trigger_interval}"
            )
            query_writer = query_writer.trigger(
                processingTime=SETTINGS.spark_streaming.trigger_interval
            )

        stream_query = query_writer.start(
            f"{SETTINGS.iceberg.catalog}.{SETTINGS.iceberg.table_identifier}"
        )

        logger.info("Streaming query started successfully. Awaiting termination...")
        stream_query.awaitTermination()
    except Exception as e:
        logger.critical(f"Error during streaming query execution: {e}", exc_info=True)
    finally:
        if spark:
            logger.info("Stopping Spark session...")
            spark.stop()
            logger.info("Spark session stopped. Application terminated.")


if __name__ == "__main__":
    main()
