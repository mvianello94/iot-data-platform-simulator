from pyspark.sql import SparkSession


def get_spark_session():
    spark: SparkSession = (
        SparkSession.builder.appName("WriteIcebergToMinIO")
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.iceberg.spark.SparkSessionCatalog",
        )
        .config("spark.sql.catalog.spark_catalog.type", "hadoop")
        .config("spark.sql.catalog.spark_catalog.warehouse", "s3a://iot-data/warehouse")
        .getOrCreate()
    )

    return spark


def create_iot_events_iceberg_table(spark: SparkSession):
    spark.sql("""
    CREATE TABLE IF NOT EXISTS spark_catalog.iot.events (
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
