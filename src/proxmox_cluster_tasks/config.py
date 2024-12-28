import os
import logging
import tomllib as toml
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class ConfigLoader:
    def __init__(self, file_path: Path = None, env_var_prefix: str = "" ):
        self.file_path = file_path or Path(__file__).parent.parent.parent /"config.toml"
        self.env_var_prefix = env_var_prefix
        self.settings = self.load_config()

    def load_config(self):
        if self.file_path.exists() is False:
            raise Exception(f"Config file not found {self.file_path}")
        with self.file_path.open("rb") as f:
            config = toml.load(f)
        config = self.override_with_env_vars(config)
        return config

    def override_with_env_vars(self, config):
        """Override settings with environment variables only if the value is not None."""
        load_dotenv()
        for section, values in config.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    env_key = f"{self.env_var_prefix}{section.upper()}_{key.upper()}"
                    env_value = os.getenv(env_key)
                    logger.debug(f"override_with_env_vars: {env_key} - {env_value}")
                    if env_value is not None:
                        config[section][key] = env_value
        return config

    def get(self, key, default=None):
        """Get a configuration value."""
        keys = key.split(".")
        value = self.settings
        try:
            for k in keys:
                value = value[k]
        except KeyError:
            return default
        return value

configuration = ConfigLoader()

if __name__ == "__main__":
    print(configuration.settings)
    print(configuration.get("api_handlers.version"))