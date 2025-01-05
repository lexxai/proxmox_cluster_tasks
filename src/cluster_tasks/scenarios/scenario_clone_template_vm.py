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
        self.vmid = int(config.get("vmid", 0))
        self.newid = config.get("newid")
        self.name = config.get("name")
        self.full = int(config.get("full", True))

    def run(self):
        print(f"Running Scenario Template: {self.template_name} at {self.source_node}")
        # Perform the specific API logic for this scenario
        try:
            # Open a connection session of the Proxmox API
            with self.api:
                # Check is VM already exists
                present = self.node_tasks.vm_status(self.node, self.newid)
                if present:
                    # If VM already exists, delete it
                    logger.info(f"VM {self.newid} already exists - Deleting...")
                    is_deleted = self.node_tasks.vm_delete(self.node, self.newid)
                    if is_deleted:
                        logger.info(f"VM {self.newid} deleted successfully")
                    else:
                        raise Exception(f"Failed to delete VM {self.newid}")
                # Clone the VM from the template
                data = {"newid": int(self.newid), "name": self.name, "full": self.full}
                is_created = self.node_tasks.vm_clone(self.node, self.vmid, data)
                if is_created:
                    logger.info(f"VM {self.newid} cloned successfully")
                else:
                    raise Exception(f"Failed to clone VM {self.newid}")
        except Exception as e:
            logger.error(f"Failed to run scenario: {e}")
