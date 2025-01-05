import logging
import time

from cluster_tasks.tasks.base_tasks import BaseTasks
from cluster_tasks.tasks.node_tasks_base import NodeTasksBase

# Creating a logger instance specific to the current module
logger = logging.getLogger("CT.{__name__}")
"""
The logger is used for logging messages related to task status monitoring and
task operations within the NodeTasks class. It is named with the format "CT.{module_name}"
to reflect the source module where the log entries are generated.
"""


class NodeTasksSync(NodeTasksBase):
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
            return self.wait_task_done_sync(node, upid)
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
            return self.wait_task_done_sync(node, upid)
        return upid
