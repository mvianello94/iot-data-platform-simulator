import logging

from config import CONFIG
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.streaming import StreamingQueryListener
from pyspark.sql.types import DoubleType, StringType, StructType

# Configure logging
logger = logging.getLogger("IoTStreamProcessor")
logger.setLevel(CONFIG.LOGGING_LEVEL)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class MyListener(StreamingQueryListener):
    def onQueryStarted(self, event):
        logger.info(f"Query started: {event.id}")

    def onQueryProgress(self, event):
        logger.debug(f"Query made progress: {event.progress.json()}")

    def onQueryTerminated(self, event):
        logger.info(
            f"Query {event.id} ended. Reason: {event.exceptionMessage or 'Normal termination.'}"
        )


logger.info("Creating Spark session...")
spark = (
    SparkSession.builder.appName("IoTStreamProcessor")
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin")
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin")
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .getOrCreate()
)

spark.streams.addListener(MyListener())
logger.info("Spark session created and listener attached.")

schema = (
    StructType()
    .add("device_id", StringType())
    .add("temperature", DoubleType())
    .add("humidity", DoubleType())
    .add("timestamp", StringType())
)

logger.info("Reading data from Kafka...")
df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "iot-events")
    .load()
)

logger.debug("Parsing JSON from Kafka messages...")
json_df = (
    df.selectExpr("CAST(value AS STRING) as json")
    .select(from_json(col("json"), schema).alias("data"))
    .select("data.*")
)

logger.info("Starting streaming write to Delta Lake...")
query = (
    json_df.writeStream.format("delta")
    .outputMode("append")
    .option("checkpointLocation", "s3a://iot-data/checkpoints")
    .start("s3a://iot-data/events")
)

logger.info("Streaming query started. Awaiting termination.")
query.awaitTermination()
