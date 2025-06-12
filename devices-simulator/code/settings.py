import os
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Settings:
    """
    Configuration settings for the IoT Data Simulator.
    Default values are defined directly in the class and can be overridden by environment variables.
    """

    # Logging
    LOGGING_LEVEL: str = os.environ.get("LOGGING_LEVEL", "INFO")

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = os.environ.get(
        "KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"
    )
    KAFKA_TOPIC: str = os.environ.get("KAFKA_TOPIC", "iot-events")

    # Devices
    DEVICE_IDS: List[str] = field(
        default_factory=lambda: os.environ.get(
            "DEVICE_IDS", "sensor-1,sensor-2,sensor-3"
        ).split(",")
    )

    # Timing
    SLEEP_INTERVAL_SECONDS: float = float(
        os.environ.get("SLEEP_INTERVAL_SECONDS", "1.0")
    )

    # Variables to simulate
    VARIABLES: List[str] = field(
        default_factory=lambda: os.environ.get(
            "VARIABLES", "temperature,humidity"
        ).split(",")
    )

    # Default ranges per variable
    DEFAULT_RANGES: Dict[str, tuple] = field(
        default_factory=lambda: {
            "temperature": (20.0, 30.0),
            "humidity": (30.0, 70.0),
            "pressure": (950.0, 1050.0),
            "power": (100.0, 1000.0),
            "co2": (400.0, 2000.0),
        }
    )

    VARIABLE_RANGES: Dict[str, tuple] = field(init=False)

    def __post_init__(self):
        self.VARIABLES = [v.strip().lower() for v in self.VARIABLES if v.strip()]
        self.VARIABLE_RANGES = {}

        for var in self.VARIABLES:
            env_min = os.environ.get(f"{var.upper()}_MIN")
            env_max = os.environ.get(f"{var.upper()}_MAX")

            if env_min is not None and env_max is not None:
                try:
                    self.VARIABLE_RANGES[var] = (float(env_min), float(env_max))
                except ValueError:
                    raise ValueError(f"Invalid numeric range for variable '{var}'.")
            elif var in self.DEFAULT_RANGES:
                self.VARIABLE_RANGES[var] = self.DEFAULT_RANGES[var]
            else:
                raise ValueError(
                    f"No range found for variable '{var}' and no default provided."
                )


SETTINGS = Settings()
