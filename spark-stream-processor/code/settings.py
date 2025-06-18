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
    raw_data_topic: str
    processed_data_topic: str
    starting_offsets: str = "latest"


class SparkStreamingSettings(CustomBaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SPARK_STREAMING_",
    )

    checkpoint_location: str
    trigger_interval: str | None = None


class Settings(CustomBaseSettings):
    logging_level: str = "INFO"

    kafka: KafkaSettings = KafkaSettings()
    spark_streaming: SparkStreamingSettings = SparkStreamingSettings()


SETTINGS = Settings()
