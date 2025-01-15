import logging
import asyncio

from cluster_tasks.scenarios.clone_template_vm_base import ScenarioCloneTemplateVmBase
from cluster_tasks.scenarios.scenario_base import ScenarioBase
from cluster_tasks.tasks.proxmox_tasks_async import (
    ProxmoxTasksAsync,
)  # Assuming there's an async version of NodeTasks

logger = logging.getLogger("CT.{__name__}")


class ScenarioSequenceScenariosAsync(ScenarioCloneTemplateVmBase):
    async def run(
        self, proxmox_tasks: ProxmoxTasksAsync, *args, **kwargs
    ) -> bool | None:
        logger.info(f"*** Running Scenario : '{self.scenario_name}'")
        # Perform the specific API logic for this scenario
        try:
            return True
        except Exception as e:
            logger.error(f"Failed to run scenario '{self.scenario_name}': {e}")
