import logging
import tomllib
from pathlib import Path
import asyncio

from cluster_tasks.configure_logging import config_logger
from cluster_tasks.tasks.node_tasks_async import NodeTasksAsync
from config.config import ConfigLoader
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI
from loader_scene import ScenarioFactory


logger = logging.getLogger("CT")
config_logger(logger)


async def main():
    config_file = Path(__file__).parent / "scenarios_configs.yaml"
    scenarios_config = ConfigLoader(file_path=config_file).settings.copy()
    # Iterate over the scenarios and run them asynchronously
    logger.debug(f"Scenarios config: {scenarios_config}")

    register_backends(["https"])

    # Change the API backend to async
    ext_api = ProxmoxAPI(
        backend_name="https", backend_type="async"
    )  # Assuming you have async support in ProxmoxAPI

    # Create an instance of the async NodeTasks class

    # Run through scenarios
    async with ext_api as api:
        node_tasks = NodeTasksAsync(api=api)  # Pass the api instance to NodeTasksAsync
        for k, v in scenarios_config.get("Scenarios").items():
            scenario_file = v.get("file")
            config = v.get("config")

            # Create scenario instance using the factory
            scenario = ScenarioFactory.create_scenario(scenario_file, config, "async")

            # Run the scenario asynchronously
            await scenario.run(node_tasks)  # Assuming `run` is now an async method


if __name__ == "__main__":
    asyncio.run(main())  # Start the event loop and run the main function asynchronously
