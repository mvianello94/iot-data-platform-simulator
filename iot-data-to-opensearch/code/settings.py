from pydantic_settings import BaseSettings, SettingsConfigDict


class CustomBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
    )


class KafkaSettings(CustomBaseSettings):
    model_config = SettingsConfigDict(env_prefix="KAFKA_")

    bootstrap_servers: str
    group_id: str
    topic: str
    starting_offsets: str = "latest"
    enable_auto_commit: bool = True


class OpenSearchSettings(CustomBaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPENSEARCH_")

    host: str
    port: str
    username: str | None = None
    password: str | None = None
    use_ssl: bool = False
    verify_certs: bool = False
    index_prefix: str


class SimulatorSettings(CustomBaseSettings):
    logging_level: str = "INFO"

    kafka: KafkaSettings = KafkaSettings()
    opensearch: OpenSearchSettings = OpenSearchSettings()


SETTINGS = SimulatorSettings()
