from pydantic_settings import BaseSettings, SettingsConfigDict


class CustomBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
    )


class KafkaSettings(CustomBaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KAFKA_",
    )

    bootstrap_servers: str
    group_id: str
    topic: str
    starting_offsets: str = "latest"


class IcebergSettings(CustomBaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ICEBERG_",
    )

    catalog: str
    table_identifier: str
    write_format_default: str = "parquet"
    format_version: int = 2
    history_expire_max_snapshots: int = 10
    history_expire_min_snapshots_to_retain: int = 1
    write_data_target_file_size_bytes: int = 536_870_912
    write_parquet_compression_codec: str = "zstd"
    optimize_rewrite_data_enabled: bool = False
    optimize_rewrite_data_target_file_size_bytes: int = 1_073_741_824


class SparkStreamingSettings(CustomBaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SPARK_STREAMING_",
    )

    checkpoint_location: str
    trigger_interval: str | None = None


class Settings(CustomBaseSettings):
    logging_level: str = "INFO"

    kafka: KafkaSettings = KafkaSettings()
    iceberg: IcebergSettings = IcebergSettings()
    spark_streaming: SparkStreamingSettings = SparkStreamingSettings()


SETTINGS = Settings()
