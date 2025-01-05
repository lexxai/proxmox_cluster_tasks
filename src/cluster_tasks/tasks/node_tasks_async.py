import asyncio
import logging

from cluster_tasks.tasks.base_tasks import BaseTasks
from cluster_tasks.tasks.node_tasks_base import NodeTasksBase

logger = logging.getLogger("CT.{__name__}")


class NodeTasksAsync(NodeTasksBase):
    """
    NodeTasks is a class for managing tasks related to virtual machines
    on a Proxmox node. This includes operations like checking task status,
    waiting for tasks to complete, and performing VM operations (e.g., clone, delete).

    Inherits from `NodeTasksBase`, which provides common functionality for API interaction.

    Methods:
        vm_status(node: str, vm_id: int) -> int:
            Retrieves the current status of a virtual machine by its ID.

        vm_delete(node: str, vm_id: int, wait: bool = True) -> str | bool | None:
            Deletes a virtual machine and optionally waits for the task to finish.

        vm_clone(node: str, vm_id: int, data: dict, wait: bool = True) -> str | bool | None:
            Clones a virtual machine and optionally waits for the task to finish.
    """

    async def vm_status(self, node: str, vm_id: int) -> int:
        """
        Retrieves the current status of a virtual machine.

        Args:
            node (str): The name of the Proxmox node.
            vm_id (int): The ID of the virtual machine.

        Returns:
            int: The status of the virtual machine (e.g., running, stopped).
        """
        status_vm = (
            await self.api.nodes(node)
            .qemu(vm_id)
            .status.current.get(filter_keys="vmid")
        )
        return int(status_vm) if status_vm else 0

    async def vm_delete(
        self, node: str, vm_id: int, wait: bool = True
    ) -> str | bool | None:
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
        upid = await self.api.nodes(node).qemu(vm_id).delete()
        if wait:
            return await self.wait_task_done_async(upid, node)
        return upid

    async def vm_clone(
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
        upid = await self.api.nodes(node).qemu(vm_id).clone.create(data=data)
        if wait:
            return await self.wait_task_done_async(upid, node)
        return upid
