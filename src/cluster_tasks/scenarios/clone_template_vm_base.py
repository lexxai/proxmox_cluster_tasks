import logging
import asyncio

from cluster_tasks.scenarios.scenario_base import ScenarioBase
from cluster_tasks.tasks.node_tasks_async import (
    NodeTasksAsync,
)  # Assuming there's an async version of NodeTasks

logger = logging.getLogger("CT.{__name__}")


class ScenarioCloneTemplateVmBase(ScenarioBase):
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
            destination_node (str): The Proxmox destination node where the VM should migrate.
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
        self.destination_node = config.get("destination_node")
        self.source_vm_id = config.get("source_vm_id")
        self.destination_vm_id = config.get("destination_vm_id")
        self.overwrite_destination = config.get("overwrite_destination", False)
        network = config.get("network", {})
        self.ip = network.get("ip")
        self.gw = network.get("gw")
        self.increase_ip = network.get("increase_ip")
        self.decrease_ip = network.get("decrease_ip")
        self.full = config.get("full", 1)

    def run(self, node_tasks: NodeTasksAsync, *args, **kwargs):
        raise NotImplementedError
