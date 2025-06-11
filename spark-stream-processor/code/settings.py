import os
from dataclasses import dataclass


@dataclass
class Settings:
    LOGGING_LEVEL: str = os.environ.get("LOGGING_LEVEL", "INFO")
    ICEBERG_CATALOG: str = os.environ.get("ICEBERG_CATALOG")


# Create a single shared config instance
SETTINGS = Settings()
