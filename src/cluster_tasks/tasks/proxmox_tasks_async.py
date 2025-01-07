import ipaddress
import logging

from cluster_tasks.tasks.proxmox_tasks_base import ProxmoxTasksBase

logger = logging.getLogger("CT.{__name__}")


class ProxmoxTasksAsync(ProxmoxTasksBase):
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

    async def vm_config_get(
        self, node: str, vm_id: int, filter_keys: str | list[str] = None
    ) -> dict | str | list | None:
        return (
            await self.api.nodes(node).qemu(vm_id).config.get(filter_keys=filter_keys)
        )

    async def vm_config_network_set(
        self, node: str, vm_id: int, config: dict, wait: bool = True
    ) -> dict | bool | None:
        id = config.get("id", 0)
        increase_ip = config.get("increase_ip")
        decrease_ip = config.get("decrease_ip")
        ip = config.get("ip")
        if ip:
            ip_list = ip.split("/")
            if len(ip_list) != 2:
                logger.error("IP address must be in CIDR format")
                return False
            try:
                ipaddress.ip_interface(ip)
            except Exception as e:
                logger.error(f"Invalid IP network address {e}")
                return None
        gw = config.get("gw")
        # get current config
        iface = f"ipconfig{id}"
        ipconfig = await self.vm_config_get(node, vm_id, filter_keys=iface)
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
        upid = await self.api.nodes(node).qemu(vm_id).config.post(data=data)
        if wait:
            if not (await self.wait_task_done_async(upid, node)):
                logger.error("Failed to set network config")
                return None
        return {"ip": config_ip, "gw": {gw or config_gw}}

    async def vm_config_tags_set(
        self,
        node: str,
        vm_id: int,
        tags: str | None,
        add: bool = True,
        wait: bool = True,
    ) -> bool:
        if tags is None:
            return True
        if add:
            current_tags = await self.vm_config_get(node, vm_id, filter_keys="tags")
            if current_tags:
                tags = f"{current_tags},{tags}"
        data = {"tags": tags}
        upid = await self.api.nodes(node).qemu(vm_id).config.post(data=data)
        if wait:
            if not (await self.wait_task_done_async(upid, node)):
                logger.error("Failed to set tags config")
                return False
        return True

    async def vm_migrate_create(
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
        upid = await self.api.nodes(node).qemu(vm_id).migrate.create(data=data)
        if wait:
            return await self.wait_task_done_async(upid, node)
        return upid

    async def get_nodes(
        self, online: bool = True, with_status: bool = False
    ) -> list[str] | list[dict]:
        nodes = await self.api.nodes.get(filter_keys=["node", "status"])
        result = []
        if nodes:
            if online:
                result = sorted(
                    [n.get("node") for n in nodes if n.get("status") == "online"]
                )
            else:
                if with_status:
                    return nodes
                else:
                    result = sorted([n.get("node") for n in nodes])
        return result

    async def get_resources(self, resource_type: str) -> list[dict]:
        request_type_map = {
            "qemu": "vm",
            "node": "node",
            "storage": "storage",
            "sdn": "sdn",
        }
        params = None
        # prepare params by filter in request
        if resource_type in request_type_map:
            params = {"type": request_type_map[resource_type]}
        resources = await self.api.cluster.resources.get(params=params)
        result = []
        for resource in resources:
            if resource.get("type") == resource_type:
                result.append(resource)
        return result

    async def get_replication_jobs(self, filter_keys: dict = None) -> list[dict]:
        jobs = await self.api.cluster.replication.get()
        if filter_keys:
            result = []
            for job in jobs:
                for key, value in filter_keys.items():
                    if job.get(key) == value:
                        result.append(job)
            return result
        return jobs

    async def create_replication_job(
        self,
        node: str,
        vm_id: int,
        target_node: int,
        data: dict = None,
        wait: bool = True,
    ) -> bool:
        if not data:
            data = {}
        data["target"] = target_node
        upid = await self.api.nodes(node).qemu(vm_id).replication.create(data=data)
        if wait:
            return await self.wait_task_done_async(upid, node)
        return upid
