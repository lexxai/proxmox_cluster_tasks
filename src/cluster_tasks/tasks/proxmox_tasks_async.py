import asyncio
import ipaddress
import logging
import time
import urllib
from tokenize import group

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
        self,
        node: str,
        vm_id: int,
        wait: bool = True,
        with_replications: bool = True,
        force_stop: bool = True,
        force_remove_resource: bool = True,
    ) -> str | bool | None:
        """
        Deletes a virtual machine and optionally waits for the deletion task to complete.

        Args:
            node (str): The name of the Proxmox node.
            vm_id (int): The ID of the virtual machine.
            wait (bool): Whether to wait for the task to complete (default is True).
            with_replications (bool): Before delete try to remove all replications of VM (default is True).
            force_stop (bool): Before delete try to stop VM (default is True).
            force_remove_resource (bool): Before delete try to remove resource (default is True).

        Returns:
            str | bool | None: The task UPID if `wait` is False;
                               `True` if task is completed successfully,
                               `False` if task timed out.
        """
        if with_replications:
            await self.remove_replication_job(vm_id, wait=True)
        if force_remove_resource:
            await self.ha_resources_delete(vid_id=vm_id)
        if force_stop:
            await self.vm_status_set(vm_id, node, "stop", wait=True)
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
        vm_id: int,
        target_node: str,
        data: dict = None,
    ):
        data_job = data.copy() if data is not None else {}
        # calculate job id
        jobs = await self.get_replication_jobs(filter_keys={"guest": vm_id})
        max_job_num = 0
        for job in jobs:
            if job.get("target") == target_node:
                logger.debug(
                    f"Replication already present for VM '{vm_id}' for '{target_node}', skip"
                )
                return False
            max_job_num = max(max_job_num, int(job.get("jobnum", 0)))
        job_id = max_job_num + 1 if len(jobs) else 0
        data_job["id"] = f"{vm_id}-{job_id}"
        data_job["target"] = target_node
        data_job["type"] = "local"
        result = await self.api.cluster.replication.create(
            data=data_job, filter_keys="_raw_"
        )
        # logger.debug(f"finished {result}")
        return result.get("success")

    async def remove_replication_job(
        self,
        vm_id: int,
        target_node: str = None,
        force: bool = None,
        keep: bool = None,
        wait: bool = False,
    ):
        jobs = await self.get_replication_jobs(filter_keys={"guest": vm_id})
        if target_node:
            jobs = [job for job in jobs if job.get("target") == target_node]
        results = []
        for job in jobs:
            job_id = job.get("id")
            data = {}
            if force is not None:
                data["force"] = int(force)
            if keep is not None:
                data["keep"] = int(keep)
            if job_id:
                result = await self.api.cluster.replication(job_id).delete(
                    data=data, filter_keys="_raw_"
                )
                results.append(result.get("success"))
        success_results = all(results)
        # logger.debug(f"success {success_results}, {wait=}")
        if wait:
            await self.wait_empty_replications(vm_id, target_node)
        return success_results

    async def is_created_replication_job(self, vm_id: int, target_node: str = None):
        jobs = await self.get_replication_jobs(filter_keys={"guest": vm_id})
        if target_node:
            for job in jobs:
                if job.get("target") == target_node:
                    return True
        return len(jobs or []) > 0

    async def wait_empty_replications(
        self, vm_id: int, target_node: str = None
    ) -> bool:
        """
        Asynchronously waits for a replication remove to complete.
        """
        start_time = time.time()
        while await self.is_created_replication_job(vm_id, target_node):
            duration = time.time() - start_time
            formatted_duration = self.format_duration(duration)
            formatted_timeout = self.format_duration(self.timeout)
            logger.info(
                f"Waiting for replication job ({vm_id} to {target_node or 'any'}) is removed... [ {formatted_duration} / {formatted_timeout} ]"
            )
            await asyncio.sleep(self.polling_interval)
            if time.time() - start_time > self.timeout:
                logger.warning(
                    f"Timeout reached while waiting for replication job is removed. ({vm_id} to {target_node or 'any'}) ..."
                )
                break
        return False

    async def ha_groups_get(self):
        return await self.api.cluster.ha.groups.get(filter_keys="group")

    async def ha_group_delete(self, group) -> bool:
        await self.api.cluster.ha.groups(group).delete()
        return True

    async def ha_group_create(
        self,
        group: str,
        nodes: str,
        data: dict = None,
        overwrite: bool = False,
    ) -> bool:
        groups = await self.ha_groups_get()
        exist = groups and (group in groups)
        if exist and not overwrite:
            return True
        if not data:
            data = {}
        data["nodes"] = nodes
        if exist and overwrite:
            await self.api.cluster.ha.groups(group).put(data=data)
            return True
        data["group"] = group
        await self.api.cluster.ha.groups.post(data=data)
        return True

    async def vm_status_current_get(self, vm_id: int, target_node: str) -> str:
        return (
            await self.api.nodes(target_node)
            .qemu(vm_id)
            .status.current.get(filter_keys="status")
        )

    async def vm_status_set(
        self, vm_id: int, node: str, status: str, wait: bool = True
    ) -> bool:
        status = status.strip().lower()
        status_current = await self.vm_status_current_get(vm_id, node)
        upid = None
        match status:
            case "start":
                if status_current and status_current == "running":
                    return True
                logger.info(f"VM {vm_id} starting on {node} ...")
                upid = await self.api.nodes(node).qemu(vm_id).status.start.post()
            case "stop":
                if status_current and status_current == "stopped":
                    return True
                logger.info(f"VM {vm_id} stopping on {node} ...")
                upid = await self.api.nodes(node).qemu(vm_id).status.stop.post()
            case _:
                logger.error(f"vm_status_set : Unknown status {status}")
        if wait and upid:
            return await self.wait_task_done_async(upid, node) is not None
        return upid is not None

    async def ha_resources_get(
        self,
        type_resource: str = "vm",
        vid_id: int = None,
        return_group_only: bool = False,
    ):
        if vid_id is None:
            resources = await self.api.cluster.ha.resources.get(
                params={"type": type_resource}
            )
            return resources

        sid = f"{type_resource}:{vid_id}"
        resources = await self.api.cluster.ha.resources(sid).get()
        if resources and return_group_only:
            return resources.get("group")
        else:
            return resources

    async def ha_resources_create(
        self,
        vid_id: int,
        group: str,
        type_resource: str = "vm",
        data: dict = None,
        overwrite: bool = False,
    ):
        sid = f"{type_resource}:{vid_id}"
        data = data.copy() if data is not None else {}
        data["group"] = group
        if overwrite:
            exist_group = await self.ha_resources_get(
                vid_id=vid_id, type_resource=type_resource, return_group_only=True
            )
            if exist_group:
                if exist_group == group:
                    return True
                logger.info(f"VM {vid_id} updating resource ...")
                result = await self.api.cluster.ha.resources(sid).put(
                    data=data, filter_keys="_raw_"
                )
                return result.get("success") if result else False
        data["sid"] = sid
        logger.info(f"VM {vid_id} creating resource ...")
        result = await self.api.cluster.ha.resources.post(
            data=data, filter_keys="_raw_"
        )
        return result.get("success") if result else False

    async def ha_resources_delete(self, vid_id: int, type_resource: str = "vm"):
        sid = f"{type_resource}:{vid_id}"
        exist_group = await self.ha_resources_get(
            vid_id=vid_id, type_resource=type_resource, return_group_only=True
        )
        if not exist_group:
            return True
        logger.info(f"VM {vid_id} deleting resource ...")
        result = await self.api.cluster.ha.resources(sid).delete(filter_keys="_raw_")
        return result.get("success") if result else False

    async def get_pools(self, pool_type: str = "qemu", pool_id: str = None) -> list:
        params = {}
        filter_keys = None
        if pool_type and pool_id:
            params["type"] = pool_type
        if pool_id:
            params["poolid"] = pool_id
            # filter_keys = "members"
        result = await self.api.pools.get(params=params, filter_keys=filter_keys)
        return result

    async def create_pool(
        self, pool_id, vm_id=None, overwrite: bool = False, data: dict = None
    ) -> bool:
        get_pools = await self.get_pools(pool_id=pool_id)
        # print(get_pools)
        if get_pools:
            get_pools = get_pools[0]
            if get_pools and pool_id:
                members = get_pools.get("members")
                members_vms = [r.get("vmid") for r in members if isinstance(r, dict)]
                vm_exist = vm_id in members_vms if vm_id else True
                if vm_exist and not overwrite:
                    return True
        data = data.copy() if data is not None else {}
        data["poolid"] = pool_id
        if not get_pools:
            logger.info(f"Creating pool '{pool_id}' ...")
            result = await self.api.pools.post(data=data, filter_keys="_raw_")
            print(result, data)
            created = result.get("success") if result else False
        else:
            created = True
        if created and vm_id:
            data["vms"] = vm_id
            data["allow-move"] = 1
            logger.info(f"Update pool '{pool_id}' members with VM {vm_id} ...")
            result = await self.api.pools.put(data=data, filter_keys="_raw_")
            return result.get("success") if result else False

        return created


async def delete_pool(self, pool_id, vm_id=None) -> bool: ...
