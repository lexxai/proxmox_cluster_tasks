import logging

from cluster_tasks.scenarios.clone_template_vm_base import ScenarioCloneTemplateVmBase
from cluster_tasks.scenarios.scenario_base import ScenarioBase
from cluster_tasks.tasks.node_tasks_sync import NodeTasksSync

logger = logging.getLogger("CT.{__name__}")


class ScenarioCloneTemplateVmSync(ScenarioCloneTemplateVmBase):
    """
    Scenario for cloning a VM from a template in a Proxmox environment.

    This scenario checks if the VM with the target ID already exists. If it does, the VM is deleted
    before cloning the template to the new VM ID. This class interacts with the Proxmox API to
    manage VM operations such as checking VM status, deleting an existing VM, and cloning a VM.

    Attributes:
        node (str): The Proxmox node where the VM resides.
        vmid (int): The ID of the VM to clone.
        newid (str): The ID of the new VM being created from the template.
        name (str): The name to assign to the new VM.
        full (int): Flag indicating whether to clone the full VM or just the template.
    """

    def run(self, node_tasks: NodeTasksSync, *args, **kwargs) -> bool | None:
        """
        Runs the scenario of cloning a VM from a template.

        This method checks if the new VM already exists, deletes it if it does, and then
        proceeds to clone the VM from the template.

        Args:
            node_tasks (NodeTasksSync): The object responsible for performing the sync operations
                                         like checking VM status, deleting a VM, and cloning a VM.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Raises:
            Exception: If the VM already exists and deletion fails, or if cloning fails.
        """
        logger.info(f"*** Running Scenario Template VM Clone: '{self.scenario_name}'")
        # Perform the specific API logic for this scenario
        try:
            # Check if the VM already exists asynchronously
            self.check_existing_destination_vm(node_tasks)

            # Clone the VM from the template asynchronously
            self.vm_clone(node_tasks)

            # Configure Network
            self.configure_network(node_tasks)

            # Configure Tags
            self.configure_tags(node_tasks)

            # Migration VM
            self.vm_migration(node_tasks)
            logger.info(f"*** Scenario '{self.scenario_name}' completed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to run scenario '{self.scenario_name}': {e}")

    @staticmethod
    def check_vm_is_exists_in_cluster(node_tasks, vm_id) -> str | None:
        resources = node_tasks.get_resources(resource_type="qemu")
        for resource in resources:
            if resource.get("vmid") == vm_id:
                return resource.get("node")
        return None

    def check_existing_destination_vm(self, node_tasks):
        logger.info(f"Checking if destination Node:'{self.destination_node}' is online")
        online_nodes = node_tasks.get_nodes(online=True)
        if self.destination_node not in online_nodes:
            raise Exception(f"Node:'{self.destination_node}' is offline")
        logger.info(f"Checking if VM {self.destination_vm_id} already exists")
        present_node = self.check_vm_is_exists_in_cluster(
            node_tasks, self.destination_vm_id
        )
        if present_node:
            if not self.overwrite_destination:
                raise Exception(
                    f"VM {self.destination_vm_id} already exists, overwrite_destination not allow to delete VM"
                )
            if present_node not in online_nodes:
                raise Exception(
                    f"VM {self.destination_vm_id} already exists on offline node:'{present_node}', cannot delete"
                )
            # If VM already exists, delete it
            logger.info(
                f"VM {self.destination_vm_id} already exists on node:'{present_node}'. Deleting..."
            )
            is_deleted = node_tasks.vm_delete(present_node, self.destination_vm_id)
            if is_deleted:
                logger.info(f"VM {self.destination_vm_id} deleted successfully")
            else:
                raise Exception(f"Failed to delete VM {self.destination_vm_id}")

    def configure_network(self, node_tasks):
        logger.info(f"Configuring Network for VM {self.destination_vm_id}")
        config = {
            "ip": self.ip,
            "gw": self.gw,
            "increase_ip": self.increase_ip,
            "decrease_ip": self.decrease_ip,
        }
        result = node_tasks.vm_config_network_set(
            self.node, self.destination_vm_id, config=config
        )
        if result is None:
            f"Failed to configure network for VM {self.destination_vm_id}: {config}"
        self.vm_network = result
        logger.info(f"Configured Network for VM {self.destination_vm_id} successfully")

    def vm_migration(self, node_tasks):
        # Migration VM
        if self.destination_node:
            logger.info(
                f"Migrating VM {self.destination_vm_id} to node: {self.destination_node}"
            )
            is_migrated = node_tasks.vm_migrate_create(
                self.node, self.destination_vm_id, self.destination_node
            )
            if is_migrated:
                logger.info(f"VM {self.destination_vm_id} migrated successfully")
            else:
                raise Exception(f"Failed to migrate VM {self.destination_vm_id}")

    def vm_clone(self, node_tasks):
        # Clone the VM from the template asynchronously
        logger.info(f"Cloning VM from {self.source_vm_id} to {self.destination_vm_id}")
        logger.debug(f"full clone: {self.full}")
        data = {
            "newid": int(self.destination_vm_id),
            "name": self.name,
            "full": self.full,
        }
        is_created = node_tasks.vm_clone(self.node, self.source_vm_id, data)
        if is_created:
            logger.info(f"VM {self.destination_vm_id} cloned successfully")
        else:
            raise Exception(f"Failed to clone VM {self.destination_vm_id}")

    def configure_tags(self, node_tasks):
        if not self.tags:
            return
        tags = self.calculate_tags(self.tags)
        logger.info(f"Configuring tags for VM {self.destination_vm_id}")
        is_configured = node_tasks.vm_config_tags_set(
            self.node, self.destination_vm_id, tags
        )
        if is_configured:
            logger.info(
                f"VM {self.destination_vm_id} configured tags:'{tags}' successfully"
            )
        else:
            f"Failed to configure tags:'{tags}' for VM {self.destination_vm_id}"
