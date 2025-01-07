import ipaddress
import logging
import time
from idlelib.sidebar import get_widget_padding

from pycparser.ply.yacc import resultlimit

from cluster_tasks.tasks.base_tasks import BaseTasks
from cluster_tasks.tasks.node_tasks_base import ProxmoxTasksBase

# Creating a logger instance specific to the current module
logger = logging.getLogger("CT.{__name__}")
"""
The logger is used for logging messages related to task status monitoring and
task operations within the NodeTasks class. It is named with the format "CT.{module_name}"
to reflect the source module where the log entries are generated.
"""


class ProxmoxTasksSync(ProxmoxTasksBase):
    """
    NodeTasks class provides functionality for interacting with tasks on a Proxmox node.
    It includes methods to check task status, wait for tasks to finish, and perform
    operations on virtual machines (VMs), such as deleting and cloning them.

    Inherits from `NodeTasksBase` for common API functionality.
    """

    def vm_status(self, node: str, vm_id: int) -> int:
        """
        Retrieves the current status of a virtual machine.

        Args:
            node (str): The name of the Proxmox node.
            vm_id (int): The ID of the virtual machine.

        Returns:
            int: The status of the virtual machine (e.g., running, stopped).
        """
        status_vm = (
            self.api.nodes(node).qemu(vm_id).status.current.get(filter_keys="vmid")
        )
        return int(status_vm) if status_vm else 0

    def vm_delete(self, node: str, vm_id: int, wait: bool = True) -> str | bool | None:
        """
        Deletes a virtual machine and optionally waits for the deletion task to complete.

        Args:
            node (str): The name of the Proxmox node.
            vm_id (int): The ID of the virtual machine.
            wait (bool): Whether to wait for the task to complete (default is True).

        Returns:
            str | bool | None: The task UPID if `wait` is False;
                               `True` if task is completed successfully,
                               `False` if task timed out.
        """
        upid = self.api.nodes(node).qemu(vm_id).delete()
        if wait:
            return self.wait_task_done_sync(upid, node)
        return upid

    def vm_clone(
        self, node: str, vm_id: int, data: dict, wait: bool = True
    ) -> str | bool | None:
        """
        Clones a virtual machine and optionally waits for the cloning task to complete.

        Args:
            node (str): The name of the Proxmox node.
            vm_id (int): The ID of the virtual machine to clone.
            data (dict): The parameters for cloning the virtual machine.
            wait (bool): Whether to wait for the task to complete (default is True).

        Returns:
            str | bool | None: The task UPID if `wait` is False;
                               `True` if the task finished successfully,
                               `False` if task timed out.
        """
        upid = self.api.nodes(node).qemu(vm_id).clone.create(data=data)
        if wait:
            return self.wait_task_done_sync(upid, node)
        return upid

    def vm_config_get(
        self, node: str, vm_id: int, filter_keys: str | list[str] = None
    ) -> dict | str | list | None:
        return self.api.nodes(node).qemu(vm_id).config.get(filter_keys=filter_keys)

    def vm_config_network_set(
        self, node: str, vm_id: int, config: dict, wait: bool = True
    ) -> dict | None:
        id = config.get("id", 0)
        increase_ip = config.get("increase_ip")
        decrease_ip = config.get("decrease_ip")
        ip = config.get("ip")
        if ip:
            ip_list = ip.split("/")
            if len(ip_list) != 2:
                logger.error("IP address must be in CIDR format")
                return None
            try:
                ipaddress.ip_interface(ip)
            except Exception as e:
                logger.error(f"Invalid IP network address {e}")
                return None
        gw = config.get("gw")
        # get current config
        iface = f"ipconfig{id}"
        ipconfig = self.vm_config_get(node, vm_id, filter_keys=iface)
        if not ipconfig:
            return None
        ipconfig = ipconfig.split(",")  # "ip={ip},gw={gw}"
        config_ip = ip or ipconfig[0].split("=")[1]
        if config_ip:
            try:
                config_ip_if = ipaddress.ip_interface(config_ip)
                if config_ip_if:
                    config_ip = f"{config_ip_if.ip + increase_ip}/{config_ip_if.network.prefixlen}"
                elif decrease_ip:
                    config_ip = f"{config_ip_if.ip - decrease_ip}/{config_ip_if.network.prefixlen}"
            except Exception as e:
                logger.error(f"Invalid IP network address {e}")
                return None
        config_gw = ipconfig[1].split("=")[1]
        new_ifconfig = f"ip={config_ip},gw={gw or config_gw}"
        data = {iface: new_ifconfig}
        upid = self.api.nodes(node).qemu(vm_id).config.post(data=data)
        if wait:
            if not (self.wait_task_done_sync(upid, node)):
                logger.error("Failed to set network config")
                return None
        return {"ip": config_ip, "gw": {gw or config_gw}}

    def vm_config_tags_set(
        self, node: str, vm_id: int, tags: str, wait: bool = True
    ) -> bool:

        data = {"tags": tags}
        upid = self.api.nodes(node).qemu(vm_id).config.post(data=data)
        if wait:
            if not (self.wait_task_done_sync(upid, node)):
                logger.error("Failed to set tags config")
                return False
        return True

    def vm_migrate_create(
        self,
        node: str,
        vm_id: int,
        target_node: str,
        data: dict = None,
        wait: bool = True,
    ) -> bool:
        if not data:
            data = {}
        data["target"] = target_node
        upid = self.api.nodes(node).qemu(vm_id).migrate.create(data=data)
        if wait:
            return self.wait_task_done_sync(upid, node)
        return upid

    def get_nodes(self, online: bool = True) -> list[str]:
        nodes = self.api.nodes.get(filter_keys=["node", "status"])
        result = []
        if nodes:
            if online:
                result = sorted(
                    [n.get("node") for n in nodes if n.get("status") == "online"]
                )
            else:
                result = sorted([n.get("node") for n in nodes])
        return result

    def get_resources(self, resource_type: str) -> list[dict]:
        resources = self.api.cluster.resources.get()
        result = []
        for resource in resources:
            if resource.get("type") == resource_type:
                result.append(resource)
        return result
