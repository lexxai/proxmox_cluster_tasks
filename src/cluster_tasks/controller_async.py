import logging
from pathlib import Path
import asyncio

from cluster_tasks.configure_logging import config_logger
from cluster_tasks.tasks.node_tasks_async import NodeTasksAsync
from config.config import ConfigLoader
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI
from loader_scene import ScenarioFactory


logger = logging.getLogger(f"CT.{__name__}")


async def scenario_run(api, scenario_config, scenario_name: str = None):
    node_tasks = NodeTasksAsync(api=api)
    scenario_file = scenario_config.get("file")
    config = scenario_config.get("config")
    # Create scenario instance using the factory
    scenario = ScenarioFactory.create_scenario(
        scenario_file, config, scenario_name, "async"
    )
    # Run the scenario asynchronously
    await scenario.run(node_tasks)  # Assuming `run` is now an async method


async def main(concurrent: bool = False):
    config_file = Path(__file__).parent / "scenarios_configs.yaml"
    scenarios_config = ConfigLoader(file_path=config_file)
    # Iterate over the scenarios and run them asynchronously
    logger.debug(f"Scenarios config: {scenarios_config}")
    backend_name = scenarios_config.get("API.backend", "https")
    register_backends(backend_name)
    # Change the API backend to async
    ext_api = ProxmoxAPI(backend_name=backend_name, backend_type="async")
    try:
        # Run through scenarios
        async with ext_api as api:
            tasks = []
            for scenario_name, scenario_config in scenarios_config.get(
                "Scenarios"
            ).items():
                if concurrent:
                    tasks.append(scenario_run(api, scenario_config, scenario_name))
                else:
                    await scenario_run(api, scenario_config, scenario_name)
            if concurrent:
                await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Controller: {e}")


if __name__ == "__main__":
    logger = logging.getLogger("CT")
    config_logger(logger)
    asyncio.run(main())  # Start the event loop and run the main function asynchronously
