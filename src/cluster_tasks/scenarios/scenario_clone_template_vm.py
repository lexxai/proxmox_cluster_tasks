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
        self.newid = config.get("name")
        self.full = config.get("full", True)

    def run(self):
        print(f"Running Scenario Template: {self.template_name} at {self.source_node}")
        # Perform the specific API logic for this scenario

        data = {"newid": self.newid, "name": self.name}
        with self.api as api:
            result = api.nodes(self.node).qemu(self.vmid).clone.create(data=data)
        logger.info(result)
