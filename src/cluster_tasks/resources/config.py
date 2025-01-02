import os
import logging
import tomllib as toml
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger("CT.{__name__}")


class ConfigLoader:
    def __init__(self, file_path: Path = None):
        self.file_path = (
            file_path or Path(__file__).parent / "resources.toml"
        )
        self.resources = self.load_config()




    def load_config(self) -> dict:
        config = {}
        if self.file_path.exists() is False:
            logger.error(f"Config file not found {self.file_path}")
            return config
        try:
            with self.file_path.open("rb") as f:
                config = toml.load(f)
        except toml.TOMLDecodeError:
            logger.error("Error of parsing config file")
        return config


    def get(self, key, default=None):
        """Get a configuration value."""
        keys = key.split(".")
        value = self.resources
        try:
            for k in keys:
                value = value[k]
        except KeyError:
            return default
        return value

api_resources = ConfigLoader()
logger.debug("LOADED RESOURCES CONFIG")

if __name__ == "__main__":
    # print(configuration.settings)
        print(api_resources.get("CLUSTER"))
