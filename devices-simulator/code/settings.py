import os
from dataclasses import dataclass


@dataclass
class Settings:
    LOGGING_LEVEL: str = os.environ.get("LOGGING_LEVEL", "INFO")


# Create a single shared settings instance
SETTINGS = Settings()
