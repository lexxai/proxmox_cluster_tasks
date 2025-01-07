import logging
import queue
from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path

from cluster_tasks.configure_logging import config_logger
from cluster_tasks.tasks.node_tasks_sync import NodeTasksSync
from config.config import ConfigLoader
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI
from loader_scene import ScenarioFactory

logger = logging.getLogger(f"CT.{__name__}")

MAX_THREADS = 16


def scenario_run_queue(api_queue, scenario_config, scenario_name: str = None):
    api = api_queue.get()
    try:
        with api as api:
            scenario_run(api, scenario_config, scenario_name)
    finally:
        api_queue.put(api)


def scenario_run(api, scenario_config, scenario_name: str = None):
    node_tasks = NodeTasksSync(api=api)
    scenario_file = scenario_config.get("file")
    config = scenario_config.get("config")
    # Create scenario instance using the factory
    scenario = ScenarioFactory.create_scenario(
        scenario_file, config, scenario_name, "sync"
    )
    # Run the scenario asynchronously
    scenario.run(node_tasks)  # Assuming `run` is now an async method


def main(concurrent: bool = False):
    config_file = Path(__file__).parent / "scenarios_configs.yaml"
    scenarios_config = ConfigLoader(file_path=config_file)
    # Iterate over the scenarios and run them
    # logger.debug(f"Scenarios config: {scenarios_config}")
    backend_name = scenarios_config.get("API.backend", "https")
    register_backends(backend_name)
    client_queue = queue.Queue()
    ext_api = None
    if concurrent:
        max_threads = min(MAX_THREADS, len(scenarios_config.get("Scenarios")))
        clients = [ProxmoxAPI(backend_name="https") for _ in range(max_threads)]
        [client_queue.put(c) for c in clients]
    else:
        ext_api = ProxmoxAPI(backend_name=backend_name, backend_type="sync")
    try:
        if concurrent:
            # Concurrent execution
            with ThreadPoolExecutor() as executor:
                tasks = [
                    executor.submit(
                        scenario_run_queue, client_queue, scenario_config, scenario_name
                    )
                    for scenario_name, scenario_config in scenarios_config.get(
                        "Scenarios"
                    ).items()
                ]
            wait(tasks)  # Wait for all tasks to complete in thread pool
        else:
            # Sequential execution
            with ext_api as api:
                for scenario_name, scenario_config in scenarios_config.get(
                    "Scenarios"
                ).items():
                    scenario_run(api, scenario_config, scenario_name)
    except Exception as e:
        logger.error(f"Controller: {e}")


if __name__ == "__main__":
    logger = logging.getLogger("CT")
    config_logger(logger)
    main()
