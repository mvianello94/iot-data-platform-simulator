import logging

from listener import StreamingListener
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    explode,
    from_json,
    to_timestamp,
    when,
)
from pyspark.sql.types import StringType, StructType
from settings import SETTINGS
from utils import get_spark_session

# Configure logging
logging.basicConfig(
    level=SETTINGS.logging_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("KafkaToKafkaProcessor")

# Minimal schema just to extract device_id and timestamp
BASE_SCHEMA = (
    StructType()
    .add("device_id", StringType(), nullable=False)
    .add("timestamp", StringType(), nullable=False)
)


def main() -> None:
    logger.info("Starting Kafka to Kafka transformer application...")

    spark: SparkSession = None
    try:
        spark = get_spark_session()
        spark.streams.addListener(StreamingListener())
        logger.info("Spark session created and listener attached.")
    except Exception as e:
        logger.critical(f"Failed to create Spark session: {e}", exc_info=True)
        exit(1)

    df: DataFrame
    try:
        df = (
            spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", SETTINGS.kafka.bootstrap_servers)
            .option("kafka.group.id", SETTINGS.kafka.group_id)
            .option("subscribe", SETTINGS.kafka.raw_data_topic)
            .option("startingOffsets", SETTINGS.kafka.starting_offsets)
            .load()
        )
        logger.info("Kafka raw stream reader initialized.")
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
    normalized_df: DataFrame = (
        parsed_df.withColumn("event_time", to_timestamp("timestamp"))
        .drop("timestamp")
        .withColumn("json_map", from_json(col("json"), "map<string,string>"))
        .select(
            "device_id",
            "event_time",
            explode(col("json_map")).alias("variable_key", "variable_value"),
        )
        .filter(~col("variable_key").isin("device_id", "timestamp"))
        .select(
            "device_id",
            "event_time",
            col("variable_key").alias("variable_id"),
            col("variable_value").alias("string_val"),
            when(
                col("variable_value").cast("double").isNotNull(),
                col("variable_value").cast("double"),
            ).alias("double_val"),
        )
    )

    logger.debug(
        "Data normalization complete. Starting write to Kafka transformed topic..."
    )

    try:
        # Prepare dataframe to write to Kafka (key,value as bytes)
        output_df = normalized_df.selectExpr(
            "CAST(device_id AS STRING) AS key", "to_json(struct(*)) AS value"
        )

        query_writer = (
            output_df.writeStream.format("kafka")
            .option("kafka.bootstrap.servers", SETTINGS.kafka.bootstrap_servers)
            .option("topic", SETTINGS.kafka.processed_data_topic)
            .option("checkpointLocation", SETTINGS.spark_streaming.checkpoint_location)
        )

        if SETTINGS.spark_streaming.trigger_interval:
            logger.info(
                f"Setting streaming trigger interval to {SETTINGS.spark_streaming.trigger_interval}"
            )
            query_writer = query_writer.trigger(
                processingTime=SETTINGS.spark_streaming.trigger_interval
            )

        stream_query = query_writer.start()

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
