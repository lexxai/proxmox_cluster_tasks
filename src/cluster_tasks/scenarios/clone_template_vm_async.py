import logging
import asyncio

from cluster_tasks.scenarios.scenario_base import ScenarioBase
from cluster_tasks.tasks.node_tasks_async import (
    NodeTasksAsync,
)  # Assuming there's an async version of NodeTasks

logger = logging.getLogger("CT.{__name__}")


class ScenarioCloneTemplateVmAsync(ScenarioBase):
    """
    Scenario for cloning a VM from a template in a Proxmox environment.

    This scenario checks if the VM with the target ID already exists. If it does, the VM is deleted
    before cloning the template to the new VM ID. This class interacts with the Proxmox API to
    manage VM operations such as checking VM status, deleting an existing VM, and cloning a VM.

    Attributes:
        node (str): The Proxmox node where the VM resides.
        vmid (int): The ID of the VM to clone.
        newid (str): The ID of the new VM being created from the template.
        name (str): The name to assign to the new VM.
        full (int): Flag indicating whether to clone the full VM or just the template.
    """

    def __init__(self):
        """
        Initializes the ScenarioCloneTemplateVmAsync class.

        This constructor calls the base class constructor to set up the necessary
        components for the scenario.
        """
        super().__init__()

    def configure(self, config):
        """
        Configures the scenario with the provided settings.

        This method reads configuration values and sets up the necessary attributes for
        the scenario to run.

        Args:
            config (dict): The configuration dictionary containing the necessary settings
                           for the scenario, including node, vmid, newid, name, and full.

        Attributes:
            node (str): The Proxmox node where the VM resides.
            vmid (int): The ID of the VM to clone.
            newid (str): The ID of the new VM to create.
            name (str): The name for the new VM.
            full (int): Flag indicating whether to clone the full VM or just the template.
        """
        self.node = config.get("node")
        self.vmid = int(config.get("vmid", 0))
        self.newid = config.get("newid")
        self.name = config.get("name")
        self.full = int(config.get("full", True))

    async def run(self, node_tasks: NodeTasksAsync, *args, **kwargs):
        """
        Runs the scenario of cloning a VM from a template asynchronously.

        This method checks if the new VM already exists, deletes it if it does, and then
        proceeds to clone the VM from the template. All operations are performed asynchronously.

        Args:
            node_tasks (NodeTasksAsync): The object responsible for performing the async operations
                                         like checking VM status, deleting a VM, and cloning a VM.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Raises:
            Exception: If the VM already exists and deletion fails, or if cloning fails.
        """
        print(f"Running Scenario Template VM Clone: {self.scenario_name}")
        # Perform the specific API logic for this scenario
        try:
            # Open a connection session of the Proxmox API
            # Check if the VM already exists asynchronously
            present = await node_tasks.vm_status(self.node, self.newid)
            if present:
                # If VM already exists, delete it asynchronously
                logger.info(f"VM {self.newid} already exists - Deleting...")
                is_deleted = await node_tasks.vm_delete(self.node, self.newid)
                if is_deleted:
                    logger.info(f"VM {self.newid} deleted successfully")
                else:
                    raise Exception(f"Failed to delete VM {self.newid}")
            # Clone the VM from the template asynchronously
            data = {"newid": int(self.newid), "name": self.name, "full": self.full}
            is_created = await node_tasks.vm_clone(self.node, self.vmid, data)
            if is_created:
                logger.info(f"VM {self.newid} cloned successfully")
            else:
                raise Exception(f"Failed to clone VM {self.newid}")
        except Exception as e:
            logger.error(f"Failed to run scenario: {e}")
