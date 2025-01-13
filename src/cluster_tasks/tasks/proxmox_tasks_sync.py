import ipaddress
import logging
import time

from cluster_tasks.tasks.proxmox_tasks_base import ProxmoxTasksBase

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
            int: id of vm if present else 0
        """
        status_vm = (
            self.api.nodes(node).qemu(vm_id).status.current.get(filter_keys="vmid")
        )
        return int(status_vm) if status_vm else 0

    def vm_delete(
        self,
        node: str,
        vm_id: int,
        wait: bool = True,
        with_replications: bool = True,
        force_stop: bool = True,
    ) -> str | bool | None:
        """
        Deletes a virtual machine and optionally waits for the deletion task to complete.

        Args:
            node (str): The name of the Proxmox node.
            vm_id (int): The ID of the virtual machine.
            wait (bool): Whether to wait for the task to complete (default is True).
            with_replications (bool): Before delete try to remove all replications of VM (default is True).
            force_stop (bool): Before delete try to stop VM (default is True).

        Returns:
            str | bool | None: The task UPID if `wait` is False;
                               `True` if task is completed successfully,
                               `False` if task timed out.
        """
        if with_replications:
            self.remove_replication_job(vm_id, wait=True)
        if force_stop:
            self.vm_status_set(vm_id, node, "stop", wait=True)
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
        resources = self.api.cluster.resources.get(params=params)
        result = []
        for resource in resources:
            if resource.get("type") == resource_type:
                result.append(resource)
        return result

    def get_replication_jobs(self, filter_keys: dict = None) -> list[dict]:
        jobs = self.api.cluster.replication.get()
        if filter_keys:
            result = []
            for job in jobs:
                for key, value in filter_keys.items():
                    if job.get(key) == value:
                        result.append(job)
            return result
        return jobs

    def create_replication_job(
        self,
        vm_id: int,
        target_node: str,
        data: dict = None,
    ):
        if not data:
            data = {}
        # calculate job id
        jobs = self.get_replication_jobs(filter_keys={"guest": vm_id})
        max_job_num = 0
        for job in jobs:
            if job.get("target") == target_node:
                logger.debug(
                    f"Replication already present for VM '{vm_id}' for '{target_node}', skip"
                )
                return False
            max_job_num = max(max_job_num, int(job.get("jobnum", 0)))
        job_id = max_job_num + 1 if len(jobs) else 0
        data["id"] = f"{vm_id}-{job_id}"
        data["target"] = target_node
        data["type"] = "local"
        result = self.api.cluster.replication.create(data=data, filter_keys="_raw_")
        # logger.debug(f"finished {result}")
        return result.get("success")

    def remove_replication_job(
        self,
        vm_id: int,
        target_node: str = None,
        force: bool = None,
        keep: bool = None,
        wait: bool = False,
    ):
        jobs = self.get_replication_jobs(filter_keys={"guest": vm_id})
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
                result = self.api.cluster.replication(job_id).delete(
                    data=data, filter_keys="_raw_"
                )
                results.append(result.get("success"))
        success_results = all(results)
        # logger.debug(f"success {success_results}, {wait=}")
        if wait:
            self.wait_empty_replications(vm_id, target_node)
        return success_results

    def is_created_replication_job(self, vm_id: int, target_node: str = None):
        jobs = self.get_replication_jobs(filter_keys={"guest": vm_id})
        if target_node:
            for job in jobs:
                if job.get("target") == target_node:
                    return True
        return len(jobs or []) > 0

    def wait_empty_replications(self, vm_id: int, target_node: str = None) -> bool:
        """
        synchronously waits for a replication remove to complete.
        """
        start_time = time.time()
        while self.is_created_replication_job(vm_id, target_node):
            duration = time.time() - start_time
            formatted_duration = self.format_duration(duration)
            formatted_timeout = self.format_duration(self.timeout)
            logger.info(
                f"Waiting for replication job ({vm_id} to {target_node or 'any'}) is removed... [ {formatted_duration} / {formatted_timeout} ]"
            )
            time.sleep(self.polling_interval)
            if time.time() - start_time > self.timeout:
                logger.warning(
                    f"Timeout reached while waiting for replication job is removed. ({vm_id} to {target_node or 'any'}) ..."
                )
                break
        return False

    def ha_groups_get(self):
        return self.api.cluster.ha.groups.get(filter_keys="group")

    def ha_group_delete(self, group) -> bool:
        self.api.cluster.ha.groups(group).delete()
        return True

    def ha_group_create(
        self,
        group: str,
        nodes: str,
        data: dict = None,
        overwrite: bool = False,
    ) -> bool:
        groups = self.ha_groups_get()
        exist = groups and (group in groups)
        if exist and not overwrite:
            return True
        if not data:
            data = {}
        data["nodes"] = nodes
        if exist and overwrite:
            self.api.cluster.ha.groups(group).put(data=data)
            return True
        data["group"] = group
        self.api.cluster.ha.groups.post(data=data)
        return True

    def vm_status_current_get(self, vm_id: int, target_node: str) -> str:
        return (
            self.api.nodes(target_node)
            .qemu(vm_id)
            .status.current.get(filter_keys="status")
        )

    def vm_status_set(
        self, vm_id: int, node: str, status: str, wait: bool = True
    ) -> bool:
        status = status.strip().lower()
        status_current = self.vm_status_current_get(vm_id, node)
        upid = None
        match status:
            case "start":
                if status_current and status_current == "running":
                    return True
                logger.info(f"VM {vm_id} starting on {node} ...")
                upid = self.api.nodes(node).qemu(vm_id).status.start.post()
            case "stop":
                if status_current and status_current == "stopped":
                    return True
                logger.info(f"VM {vm_id} stopping on {node} ...")
                upid = self.api.nodes(node).qemu(vm_id).status.stop.post()
            case _:
                logger.error(f"vm_status_set : Unknown status {status}")
        if wait and upid:
            return self.wait_task_done_sync(upid, node) is not None
        return upid is not None
    
    
    def ha_resources_get(
        self,
        type_resource: str = "vm",
        vid_id: int = None,
        return_group_only: bool = False,
    ):

        resources = self.api.cluster.ha.resources.get(
            params={"type": type_resource}
        )
        if vid_id is not None:
            sid = f"vm:{vid_id}"
            if return_group_only:
                return [r.get("group") for r in resources if r.get("sid") == sid]
            else:
                return [r for r in resources if r.get("sid") == sid]
        return resources

