import logging

from cluster_tasks.scenarios.scenario_base import ScenarioBase
from ext_api.proxmox_api import ProxmoxAPI

logger = logging.getLogger("CT.{__name__}")


class ScenarioCloneTemplateVm(ScenarioBase):
    def __init__(self, api: ProxmoxAPI):
        super().__init__(api)
        self.destination_name = None
        self.source_node = None
        self.template_name = None

    def configure(self, config):
        self.node = config.get("node")
        self.vmid = config.get("vmid")
        self.newid = config.get("newid")
        self.name = config.get("name")
        self.full = int(config.get("full", True))

    def run(self):
        print(f"Running Scenario Template: {self.template_name} at {self.source_node}")
        # Perform the specific API logic for this scenario

        # data = {"newid": int(self.newid), "name": self.name, "full": self.full}
        with self.api as api:
            present = (
                api.nodes(self.node)
                .qemu(self.newid)
                .status.current.get(filter_keys="vmid")
            )
            logger.info(f"result: {present} {self.newid} {self.newid==present}")
            if present and int(present) == int(self.newid):
                logger.info(f"VM {self.newid} already exists - Deleteting...")
                upid = api.nodes(self.node).qemu(self.newid).delete()
                logger.info(f"result: {upid}")
                self.wait_task_done(api, self.node, upid)
            data = {"newid": int(self.newid), "name": self.name, "full": self.full}
            upid = api.nodes(self.node).qemu(self.vmid).clone.create(data=data)
            logger.info(f"result: {upid}, data: {data}")
            self.wait_task_done(api, self.node, upid)
            logger.info(f"VM {self.newid} created")
