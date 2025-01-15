import logging
import asyncio


from cluster_tasks.scenarios.sequence_scenarios_base import (
    ScenarioSequenceScenariosBase,
)
from cluster_tasks.tasks.proxmox_tasks_async import (
    ProxmoxTasksAsync,
)  # Assuming there's an async version of NodeTasks

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
            if self.destination_nodes == "all-online":
                self.destination_nodes = await proxmox_tasks.get_nodes(online=True)

            for node in self.destination_nodes:
                logger.info(f"Running scenario on node: {node}")
            return True
        except Exception as e:
            logger.error(f"Failed to run scenario '{self.scenario_name}': {e}")
