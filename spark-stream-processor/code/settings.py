from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    bootstrap_servers: str = "kafka:9092"
    topic: str = "iot-events"
    starting_offsets: str = "latest"

    model_config = SettingsConfigDict(
        env_prefix="KAFKA_",
        case_sensitive=False,
    )


class IcebergSettings(BaseSettings):
    catalog: str = "spark_catalog"
    table_identifier: str = "iot.events"
    write_format_default: str = "parquet"
    format_version: int = 2
    history_expire_max_snapshots: int = 10
    history_expire_min_snapshots_to_retain: int = 1
    write_data_target_file_size_bytes: int = 536_870_912
    write_parquet_compression_codec: str = "zstd"
    optimize_rewrite_data_enabled: bool = False
    optimize_rewrite_data_target_file_size_bytes: int = 1_073_741_824

    model_config = SettingsConfigDict(
        env_prefix="ICEBERG_",
        case_sensitive=False,
    )


class SparkStreamingSettings(BaseSettings):
    checkpoint_location: str = "s3a://iot-data/checkpoints/events"
    streaming_trigger_interval: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="SPARK_STREAMING_",
        case_sensitive=False,
    )


class Settings(BaseSettings):
    logging_level: str = "INFO"

    kafka: KafkaSettings = KafkaSettings()
    iceberg: IcebergSettings = IcebergSettings()
    spark_streaming: SparkStreamingSettings = SparkStreamingSettings()

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
    )


SETTINGS = Settings()
