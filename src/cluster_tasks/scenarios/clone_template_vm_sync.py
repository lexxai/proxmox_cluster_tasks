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

    def run(self, node_tasks: NodeTasksSync, *args, **kwargs):
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
        logger.info(f"Running Scenario Template VM Clone: {self.scenario_name}")
        # Perform the specific API logic for this scenario
        try:
            # Check if the VM already exists asynchronously
            self.check_existing_destination_vm(node_tasks)

            # Clone the VM from the template asynchronously
            self.vm_clone(node_tasks)

            # Configure Network
            self.configure_network(node_tasks)

            # Migration VM
            self.vm_migration(node_tasks)
            logger.info(f"Scenario {self.scenario_name} completed successfully")
        except Exception as e:
            logger.error(f"Failed to run scenario: {e}")

    def check_existing_destination_vm(self, node_tasks):
        logger.info(f"Checking if VM {self.destination_vm_id} already exists")
        nodes = [self.destination_node, self.node]
        additional_nodes = node_tasks.get_nodes(online=True)
        for node in additional_nodes:
            if node not in nodes:  # Avoid duplicates
                nodes.append(node)
        logger.debug(f"Nodes: {nodes}")
        for node in nodes:
            present = node_tasks.vm_status(node, self.destination_vm_id)
            if present:
                if not self.overwrite_destination:
                    raise Exception(
                        f"VM {self.destination_vm_id} already exists, overwrite_destination not allow to delete VM"
                    )
                # If VM already exists, delete it
                logger.info(
                    f"VM {self.destination_vm_id} already exists on node:'{node}'. Deleting..."
                )
                is_deleted = node_tasks.vm_delete(node, self.destination_vm_id)
                if is_deleted:
                    logger.info(f"VM {self.destination_vm_id} deleted successfully")
                    break
                else:
                    raise Exception(f"Failed to delete VM {self.destination_vm_id}")

    def configure_network(self, node_tasks):
        logger.info(f"Configuring Network for VM {self.destination_vm_id}")
        config = {
            "ip": self.ip,
            "gw": self.gw,
            "increase_ip": self.increase_ip,
            "decrease_ip": self.decrease_ip,
            "full": self.full,
        }
        if not node_tasks.vm_config_network_set(
            self.node, self.destination_vm_id, config=config
        ):
            raise Exception("Failed to configure network for VM")
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
