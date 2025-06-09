import os
from dataclasses import dataclass


@dataclass
class Config:
    LOGGING_LEVEL: str = os.environ.get("LOGGING_LEVEL", "INFO")


# Create a single shared config instance
CONFIG = Config()
