import os
import logging
import tomllib as toml
import yaml
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger("CT.{__name__}")


class ConfigLoader:
    def __init__(self, file_path: Path = None, env_var_prefix: str = ""):
        self.config_folder = self.find_config_folder()
        self.file_path = file_path or self.config_folder / "config.toml"
        self.env_var_prefix = env_var_prefix
        self.settings = self.load_config()
        self.build_token()

    @staticmethod
    def find_config_folder():
        run_folder = Path(os.getcwd() or ".")
        config_folder = Path("configs")
        config_folders = [
            run_folder,
            Path(__file__).parent.parent.parent.parent,
            Path(__file__).parent.parent.parent,
            Path(__file__).parent.parent,
            Path(__file__).parent,
        ]
        for folder in config_folders:
            folder = folder.joinpath(config_folder)
            if folder.is_dir():
                config_folder = folder
                break
        if config_folder.exists() is False:
            logger.error(f"Config folder not found")
            config_folder = None
        # else:
        #     print(f"*** Config folder found in '{config_folder}'")
        return config_folder

    def build_token(self):
        if "API" not in self.settings:
            return
        token_id = self.get("API.TOKEN_ID")
        token_secret = self.get("API.TOKEN_SECRET")
        token = [token_id, token_secret]
        if not all(token):
            return
        self.settings["API"]["TOKEN"] = "=".join(token)

    def load_config(self) -> dict:
        config = {}
        if self.file_path.exists() is False:
            logger.error(f"Config file not found {self.file_path}")
            return config
        if self.file_path.suffix == ".yaml":
            try:
                with self.file_path.open("rb") as f:
                    config = yaml.safe_load(f)
                return config
            except Exception as e:
                logger.error(f"Error of parsing config file {e}")
        elif self.file_path.suffix == ".toml":
            try:
                with self.file_path.open("rb") as f:
                    config = toml.load(f)
                config = self.override_with_env_vars(config)
            except Exception:
                logger.error("Error of parsing config file")
        return config

    @staticmethod
    def convert_to_bool(value: str) -> bool | str:
        """
        Convert a string value to a boolean if possible.

        Args:
            value (str): The string to convert.

        Returns:
            bool | str: The boolean value if conversion is successful,
                        otherwise the original string.
        """
        value = value.strip()
        match value.lower():
            case "true":
                return True
            case "false":
                return False
            case _:
                return value

    @staticmethod
    def convert_to_list(value: any) -> list | str:
        if not isinstance(value, str) or (value.startswith("[") is False):
            return value
        values = value.strip(" []").split(",")
        return [v.strip(" \"'") for v in values]

    def override_with_env_vars(self, config: dict) -> dict:
        """
        Override configuration values with environment variables.

        For each configuration section and key, check if there is an environment
        variable with the same name (with a prefix if specified). If the
        environment variable exists, its value is used instead of the
        configuration value. Boolean values are converted to boolean type.

        Args:
            config (dict): The configuration dictionary to override.

        Returns:
            dict: The configuration dictionary with overridden values.
        """
        load_dotenv()
        for section, values in config.items():
            # print(f"override_with_env_vars: {section} - {values}")
            if isinstance(values, dict):
                for key, value in values.items():
                    env_key = f"{self.env_var_prefix}{section.upper()}_{key.upper()}"
                    env_value = os.getenv(env_key)
                    # print(f"override_with_env_vars: {env_key} - {env_value}")
                    if env_value is not None:
                        env_value = self.convert_to_bool(env_value)
                        config[section][key] = env_value
            else:
                env_key = f"{self.env_var_prefix}{section.upper()}"
                env_value = os.getenv(env_key)
                # print(f"override_with_env_vars: {env_key} - {env_value}")
                if env_value is not None:
                    env_value = self.convert_to_bool(env_value)
                    env_value = self.convert_to_list(env_value)
                    config[section] = env_value
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
# configuration = None


def initialize(file_path: Path = None):
    global configuration
    if not file_path or file_path.is_file() is False:
        logger.error(f"Config file ({file_path}) not found")
        return None
    configuration = ConfigLoader(file_path=file_path)
    return len(configuration.settings.keys())


if __name__ == "__main__":
    # print(configuration.settings)
    print(configuration.get("NODES"))
