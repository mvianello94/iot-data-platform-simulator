from pyspark.sql import SparkSession
from settings import SETTINGS


def get_spark_session() -> SparkSession:
    spark: SparkSession = SparkSession.builder.appName("StreamProcessor").getOrCreate()
    return spark


def create_iot_events_iceberg_table(spark: SparkSession):
    spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {SETTINGS.ICEBERG_CATALOG}.iot.events (
        device_id STRING,
        temperature DOUBLE,
        humidity DOUBLE,
        event_time TIMESTAMP,
        year INT,
        month INT,
        day INT
    )
    USING ICEBERG
    PARTITIONED BY (year, month, day)
    """)
