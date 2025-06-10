import logging

from config import CONFIG
from listener import StreamingListener
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, dayofmonth, from_json, month, to_timestamp, year
from pyspark.sql.types import DoubleType, StringType, StructType
from utils import create_iot_events_iceberg_table, get_spark_session

# Configura logging
logging.basicConfig(
    level=CONFIG.LOGGING_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("IoTStreamProcessor")


# Crea SparkSession configurata per Apache Iceberg su MinIO
logger.info("Creating Spark session for Iceberg...")
spark: SparkSession = get_spark_session()

spark.streams.addListener(StreamingListener())
logger.info("Spark session created and listener attached.")

# Schema per i messaggi JSON
schema = (
    StructType()
    .add("device_id", StringType())
    .add("temperature", DoubleType())
    .add("humidity", DoubleType())
    .add("timestamp", StringType())
)

# Crea la tabella Iceberg se non esiste
logger.info("Creating Iceberg table if not exists...")
create_iot_events_iceberg_table(spark=spark)

# Leggi dallo stream Kafka
logger.info("Reading data from Kafka topic 'iot-events'...")
df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "iot-events")
    .load()
)

# Parsing JSON e aggiunta colonne temporali
logger.debug("Parsing JSON and adding partition columns...")
json_df = (
    df.selectExpr("CAST(value AS STRING) as json")
    .select(from_json(col("json"), schema).alias("data"))
    .select("data.*")
)

transformed_df = (
    json_df.withColumn("event_time", to_timestamp(col("timestamp")))
    .withColumn("year", year(col("event_time")))
    .withColumn("month", month(col("event_time")))
    .withColumn("day", dayofmonth(col("event_time")))
    .drop("timestamp")
)

# Scrittura su Iceberg
logger.info("Starting streaming write to Iceberg table 'iot.events'...")
try:
    query = (
        transformed_df.writeStream.format("iceberg")
        .outputMode("append")
        .option("checkpointLocation", "s3a://iot-data/checkpoints/events")
        .start("spark_catalog.iot.events")
    )

    logger.info("Streaming query started. Awaiting termination.")
    query.awaitTermination()
except Exception as e:
    logger.exception(e)
