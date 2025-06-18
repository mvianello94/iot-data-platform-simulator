import logging

from listener import StreamingListener
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    dayofmonth,
    from_json,
    month,
    to_timestamp,
    year,
)
from pyspark.sql.types import DoubleType, StringType, StructType
from settings import SETTINGS
from utils import create_iot_telemetry_iceberg_table, get_spark_session

# Configure logging
logging.basicConfig(
    level=SETTINGS.logging_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ProcessedKafkaToIceberg")

# Schema of already normalized data in Kafka
PROCESSED_SCHEMA = (
    StructType()
    .add("device_id", StringType(), nullable=False)
    .add("event_time", StringType(), nullable=False)  # will be converted to timestamp
    .add("variable_id", StringType(), nullable=False)
    .add("string_val", StringType(), nullable=True)
    .add("double_val", DoubleType(), nullable=True)
)


def main() -> None:
    logger.info("Starting Processed Kafka to Iceberg application...")

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
            .option("kafka.group.id", SETTINGS.kafka.group_id)
            .option("subscribe", SETTINGS.kafka.topic)
            .option("startingOffsets", SETTINGS.kafka.starting_offsets)
            .load()
        )
        logger.info("Kafka processed stream reader initialized.")
    except Exception as e:
        logger.critical(f"Failed to initialize Kafka stream reader: {e}", exc_info=True)
        if spark:
            spark.stop()
        exit(1)

    logger.debug("Parsing processed Kafka JSON payload...")

    parsed_df: DataFrame = (
        df.selectExpr("CAST(value AS STRING) as json")
        .select(from_json(col("json"), PROCESSED_SCHEMA).alias("data"))
        .select("data.*")
        .withColumn("event_time", to_timestamp("event_time"))
        .withColumn("year", year("event_time"))
        .withColumn("month", month("event_time"))
        .withColumn("day", dayofmonth("event_time"))
    )

    logger.debug("Processed data parsing complete. Starting write to Iceberg...")

    try:
        query_writer = (
            parsed_df.writeStream.format("iceberg")
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
