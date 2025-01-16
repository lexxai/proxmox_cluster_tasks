import copy
import logging
import asyncio


from cluster_tasks.scenarios.sequence_scenarios_base import (
    ScenarioSequenceScenariosBase,
)
from cluster_tasks.tasks.proxmox_tasks_async import (
    ProxmoxTasksAsync,
)  # Assuming there's an async version of NodeTasks
from config_loader.config import ConfigLoader

logger = logging.getLogger("CT.{__name__}")


class ScenarioSequenceScenariosAsync(ScenarioSequenceScenariosBase):
    async def run(
        self, proxmox_tasks: ProxmoxTasksAsync, *args, **kwargs
    ) -> bool | None:
        logger.info(f"*** Running Scenario : '{self.scenario_name}'")
        if not self.configured:
            raise Exception("Scenario not configured")
        # Perform the specific API logic for this scenario
        try:
            if isinstance(self.destination_nodes, str):
                match self.destination_nodes:
                    case "all-online":
                        self.destination_nodes = await proxmox_tasks.get_nodes(
                            online=True
                        )
                    case "all":
                        self.destination_nodes = await proxmox_tasks.get_nodes(
                            online=False
                        )

            config = ConfigLoader(file_path=self.file)
            for id, node in enumerate(self.destination_nodes):
                logger.info(f"Running scenario on node: {node}")
                logger.info(config.settings)
                config_scenario = self.prepare_config(
                    copy.deepcopy(config.settings), node, id
                )
                logger.info(config_scenario)
                # await self.run_scenario(proxmox_tasks, config_scenario)
            return True
        except Exception as e:
            logger.error(f"Failed to run scenario '{self.scenario_name}': {e}")