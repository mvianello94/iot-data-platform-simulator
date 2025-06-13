import os
from typing import Dict, List, Tuple

from pydantic import field_validator, model_validator
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
    topic: str


class SimulationSettings(CustomBaseSettings):
    """
    Configuration for the IoT Data Simulator.

    You can override any default using environment variables.
    - DEVICE_IDS: comma-separated list of device IDs (default: "sensor-1,sensor-2,sensor-3")
    - VARIABLES: comma-separated list of variables to simulate (default: "temperature,humidity")
    - {VARIABLE}_MIN and {VARIABLE}_MAX: override min/max range for a given variable
      Example: TEMPERATURE_MIN=18.5, HUMIDITY_MAX=80

    Supported variables with default ranges:
    - temperature: (20.0, 30.0)
    - humidity: (30.0, 70.0)
    - pressure: (950.0, 1050.0)
    - power: (100.0, 1000.0)
    - co2: (400.0, 2000.0)

    Examples (in .env or shell):
    ----------------------------------------
    DEVICE_IDS=sensor-a,sensor-b
    VARIABLES=temperature,power
    TEMPERATURE_MIN=15.0
    TEMPERATURE_MAX=25.0
    POWER_MIN=200.0
    POWER_MAX=800.0
    ----------------------------------------

    The final variable_ranges dict will be computed based on the selected VARIABLES,
    pulling from environment overrides or falling back to default_ranges.
    """

    model_config = SettingsConfigDict(env_prefix="")

    sleep_interval_seconds: float = 1.0
    device_ids: List[str] = ["sensor-1", "sensor-2", "sensor-3"]
    variables: List[str] = ["temperature", "humidity", "pressure", "power", "co2"]
    default_ranges: Dict[str, Tuple[float, float]] = {
        "temperature": (20.0, 30.0),
        "humidity": (30.0, 70.0),
        "pressure": (950.0, 1050.0),
        "power": (100.0, 1000.0),
        "co2": (400.0, 2000.0),
    }
    variable_ranges: Dict[str, Tuple[float, float]] = {}

    @field_validator("device_ids", mode="before")
    def split_device_ids(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("variables", mode="before")
    def split_variables(cls, v):
        if isinstance(v, str):
            return [item.strip().lower() for item in v.split(",") if item.strip()]
        return [item.lower() for item in v]

    @model_validator(mode="after")
    def resolve_variable_ranges(self) -> "SimulationSettings":
        ranges = {}

        for var in self.variables:
            env_min = self.__read_env_float(f"{var.upper()}_MIN")
            env_max = self.__read_env_float(f"{var.upper()}_MAX")

            if env_min is not None and env_max is not None:
                ranges[var] = (env_min, env_max)
            elif var in self.default_ranges:
                ranges[var] = self.default_ranges[var]
            else:
                raise ValueError(
                    f"No range found or default provided for variable '{var}'."
                )

        self.variable_ranges = ranges
        return self

    def __read_env_float(self, key: str):
        val = os.getenv(key)
        if val is not None:
            try:
                return float(val)
            except ValueError:
                raise ValueError(f"Invalid float for env var {key}: '{val}'")
        return None


class SimulatorSettings(CustomBaseSettings):
    logging_level: str = "INFO"

    kafka: KafkaSettings = KafkaSettings()
    simulation: SimulationSettings = SimulationSettings()


SETTINGS = SimulatorSettings()
