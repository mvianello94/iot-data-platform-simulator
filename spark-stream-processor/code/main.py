import logging

from listener import StreamingListener
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, dayofmonth, from_json, month, to_timestamp, year
from pyspark.sql.types import DoubleType, StringType, StructType
from settings import SETTINGS
from utils import create_iot_events_iceberg_table, get_spark_session

# Configure logging
logging.basicConfig(
    level=SETTINGS.LOGGING_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("IoTStreamProcessor")


# Schema for JSON messages coming from Kafka
IOT_EVENTS_SCHEMA = (
    StructType()
    .add("device_id", StringType(), nullable=False)
    .add("temperature", DoubleType())
    .add("humidity", DoubleType())
    .add("timestamp", StringType(), nullable=False)
)


def main():
    """
    Main function to initialize Spark, read from Kafka, process IoT events,
    and write them to an Apache Iceberg table.
    """
    logger.info("Starting IoT Stream Processor application...")

    # Create SparkSession configured for Apache Iceberg on MinIO
    logger.info("Creating Spark session for Iceberg...")
    try:
        spark: SparkSession = get_spark_session()
        spark.streams.addListener(
            StreamingListener()
        )  # Attach custom listener for debugging purpose
        logger.info("Spark session created and listener attached.")
    except Exception as e:
        logger.critical(
            f"Failed to create Spark session or attach listener: {e}", exc_info=True
        )
        exit(1)  # Exit if Spark session cannot be initialized

    # Create the Iceberg table if it doesn't exist
    logger.info(
        f"Ensuring Iceberg table '{SETTINGS.ICEBERG_CATALOG}.{SETTINGS.ICEBERG_TABLE_IDENTIFIER}' exists..."
    )
    try:
        create_iot_events_iceberg_table(
            spark=spark,
            table_identifier=f"{SETTINGS.ICEBERG_CATALOG}.{SETTINGS.ICEBERG_TABLE_IDENTIFIER}",
        )
        logger.info("Iceberg table check/creation complete.")
    except Exception as e:
        logger.critical(f"Failed to create or verify Iceberg table: {e}", exc_info=True)
        spark.stop()
        exit(1)

    # Read from Kafka stream
    logger.info(
        f"Reading data from Kafka topic '{SETTINGS.KAFKA_TOPIC}' from brokers '{SETTINGS.KAFKA_BOOTSTRAP_SERVERS}'..."
    )
    try:
        df = (
            spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", SETTINGS.KAFKA_BOOTSTRAP_SERVERS)
            .option("subscribe", SETTINGS.KAFKA_TOPIC)
            .option("startingOffsets", SETTINGS.KAFKA_STARTING_OFFSETS)
            .load()
        )
        logger.info("Kafka stream reader initialized.")
    except Exception as e:
        logger.critical(f"Failed to initialize Kafka stream reader: {e}", exc_info=True)
        spark.stop()
        exit(1)

    # Parse JSON and add temporal columns for partitioning
    logger.debug(
        "Parsing JSON payload and adding temporal columns (year, month, day)..."
    )
    json_df = (
        df.selectExpr(
            "CAST(value AS STRING) as json"
        )  # Cast binary Kafka value to string
        .select(from_json(col("json"), IOT_EVENTS_SCHEMA).alias("data"))  # Parse JSON
        .select("data.*")  # Select all fields from the parsed 'data' struct
    )

    # Transform: Convert timestamp string to actual timestamp and extract date parts
    transformed_df = (
        json_df.withColumn(
            "event_time", to_timestamp(col("timestamp"))
        )  # Convert string to timestamp
        .withColumn("year", year(col("event_time")))
        .withColumn("month", month(col("event_time")))
        .withColumn("day", dayofmonth(col("event_time")))
        .drop("timestamp")  # Drop the original string timestamp column
    )
    logger.debug("Data transformation pipeline established.")

    # Write processed data to Iceberg
    logger.info(
        f"Starting streaming write to Iceberg table '{SETTINGS.ICEBERG_CATALOG}.{SETTINGS.ICEBERG_TABLE_IDENTIFIER}' with checkpoint '{SETTINGS.CHECKPOINT_LOCATION}'..."
    )
    try:
        query = (
            transformed_df.writeStream.format("iceberg")
            .outputMode("append")  # Append new data to the table
            .option("checkpointLocation", SETTINGS.CHECKPOINT_LOCATION)
        )
        # Apply streaming trigger if configured
        if SETTINGS.STREAMING_TRIGGER_INTERVAL:
            logger.info(
                f"Setting streaming trigger interval to {SETTINGS.STREAMING_TRIGGER_INTERVAL}"
            )
            query = query.trigger(processingTime=SETTINGS.STREAMING_TRIGGER_INTERVAL)

        stream_query = query.start(
            f"{SETTINGS.ICEBERG_CATALOG}.{SETTINGS.ICEBERG_TABLE_IDENTIFIER}"
        )

        logger.info(
            "Streaming query started successfully. Awaiting termination signal..."
        )
        stream_query.awaitTermination()  # Block until the query terminates
    except Exception as e:
        logger.critical(f"Error during streaming query execution: {e}", exc_info=True)
    finally:
        logger.info("Stopping Spark session...")
        spark.stop()
        logger.info("Spark session stopped. Application terminated.")


if __name__ == "__main__":
    main()
