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

        This method initializes the scenario by reading configuration values from the
        provided dictionary and setting up the necessary attributes. If certain values
        are not explicitly set, defaults are copied from the source VM configuration.

        Args:
            config (dict): A dictionary containing the configuration settings. The expected keys are:
                - node (str): The Proxmox node where the VM resides.
                - source_vm_id (int): The ID of the source VM to clone.
                - destination_vm_id (int): The ID of the new VM to create.
                - name (str): The name for the new VM.
                - ip (str, optional): The base IP address with its mask (e.g., "192.0.2.12/24") for the new VM.
                                      If not provided, it will be copied from the source VM's IP and modified
                                      using `increase_ip` or `decrease_ip` if specified.
                - gw (str, optional): The gateway (GW) IP address for the new VM. If not provided,
                                      it will be copied from the source VM's GW.
                - increase_ip (int, optional): The value to increment the IP address by. If `ip` is not provided,
                                               this value will modify the source VM's IP to compute the new IP.
                - decrease_ip (int, optional): The value to decrement the IP address by. If `ip` is not provided,
                                               this value will modify the source VM's IP to compute the new IP.
                - full (int, optional): Flag indicating whether to clone the full VM or just the template.
                                        Defaults to 1 (full clone).

        Attributes:
            node (str): The Proxmox node where the VM resides.
            source_vm_id (int): The ID of the source VM to clone.
            destination_vm_id (int): The ID of the new VM to create.
            name (str): The name for the new VM.
            ip (str): The final IP address with its mask for the new VM, derived from the configuration or the source VM.
            gw (str): The final gateway IP address for the new VM, derived from the configuration or the source VM.
            increase_ip (int): The value to increment the IP address by.
            decrease_ip (int): The value to decrement the IP address by.
            full (int): Flag indicating whether to clone the full VM or just the template.

        Notes:
            - The `ip` must always include the network mask (e.g., "192.0.2.12/24").
            - If `ip` is not set, it defaults to the source VM's IP with its mask, potentially modified by `increase_ip` or `decrease_ip`.
            - If `gw` is not set, it defaults to the source VM's gateway IP.
            - Ensure `increase_ip` and `decrease_ip` are not used simultaneously to avoid conflicts.
        """
        self.name = config.get("name")
        self.node = config.get("node")
        self.source_vm_id = config.get("source_vm_id")
        self.destination_vm_id = config.get("destination_vm_id")
        network = config.get("network", {})
        self.ip = network.get("ip")
        self.gw = network.get("gw")
        self.increase_ip = network.get("increase_ip")
        self.decrease_ip = network.get("decrease_ip")
        self.full = config.get("full", 1)

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
        logger.info(f"Running Scenario Template VM Clone: {self.scenario_name}")
        # Perform the specific API logic for this scenario
        try:
            # Open a connection session of the Proxmox API
            # Check if the VM already exists asynchronously
            present = await node_tasks.vm_status(self.node, self.destination_vm_id)
            if present:
                # If VM already exists, delete it asynchronously
                logger.info(f"VM {self.destination_vm_id} already exists - Deleting...")
                is_deleted = await node_tasks.vm_delete(
                    self.node, self.destination_vm_id
                )
                if is_deleted:
                    logger.info(f"VM {self.destination_vm_id} deleted successfully")
                else:
                    raise Exception(f"Failed to delete VM {self.destination_vm_id}")
            # Clone the VM from the template asynchronously
            logger.info(
                f"Cloning VM from {self.source_vm_id} to {self.destination_vm_id}"
            )
            data = {
                "newid": int(self.destination_vm_id),
                "name": self.name,
                "full": self.full,
            }
            is_created = await node_tasks.vm_clone(self.node, self.source_vm_id, data)
            if is_created:
                logger.info(f"VM {self.destination_vm_id} cloned successfully")
            else:
                raise Exception(f"Failed to clone VM {self.destination_vm_id}")
            logger.info(f"Configuring Network for VM {self.destination_vm_id}")
            config = {
                "ip": self.ip,
                "gw": self.gw,
                "increase_ip": self.increase_ip,
                "decrease_ip": self.decrease_ip,
                "full": self.full,
            }
            if not await node_tasks.vm_config_network_set(
                self.node, self.destination_vm_id, config=config
            ):
                raise Exception("Failed to configure network for VM")
            logger.info(
                f"Configured Network for VM {self.destination_vm_id} successfully"
            )
            logger.info(f"Scenario {self.scenario_name} completed successfully")
        except Exception as e:
            logger.error(f"Failed to run scenario: {e}")
