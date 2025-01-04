import logging
import tomllib
from pathlib import Path

from cluster_tasks.configure_logging import config_logger
from config.config import ConfigLoader
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI
from loader_scene import ScenarioFactory


logger = logging.getLogger("CT")
config_logger(logger)


def main():
    config_file = Path(__file__).parent / "scenarios_configs.yaml"
    scenarios_config = ConfigLoader(file_path=config_file).settings.copy()
    # Iterate over the scenarios and run them
    logger.debug(f"Scenarios config: {scenarios_config}")

    register_backends(["https"])
    api = ProxmoxAPI(backend_name="https", backend_type="sync")
    for k, v in scenarios_config.get("Scenarios").items():
        scenario_file = v.get("file")
        config = v.get("config")

        # Create scenario instance using the factory
        scenario = ScenarioFactory.create_scenario(scenario_file, api, config)

        # Run the scenario
        scenario.run()


if __name__ == "__main__":
    main()
