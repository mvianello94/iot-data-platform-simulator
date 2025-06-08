from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import DoubleType, StringType, StructType

spark = (
    SparkSession.builder.appName("IoTStreamProcessor")
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin")
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin")
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .getOrCreate()
)

schema = (
    StructType()
    .add("device_id", StringType())
    .add("temperature", DoubleType())
    .add("humidity", DoubleType())
    .add("timestamp", StringType())
)

df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "iot-events")
    .load()
)

json_df = (
    df.selectExpr("CAST(value AS STRING) as json")
    .select(from_json(col("json"), schema).alias("data"))
    .select("data.*")
)

query = (
    json_df.writeStream.format("delta")
    .outputMode("append")
    .option("checkpointLocation", "s3a://iot-data/checkpoints")
    .start("s3a://iot-data/events")
)

query.awaitTermination()
