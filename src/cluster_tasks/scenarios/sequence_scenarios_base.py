import logging
import asyncio
import re
from os.path import split

from cluster_tasks.scenarios.scenario_base import ScenarioBase
from cluster_tasks.tasks.proxmox_tasks_async import (
    ProxmoxTasksAsync,
)  # Assuming there's an async version of NodeTasks

logger = logging.getLogger("CT.{__name__}")


class SequenceScenariosBase(ScenarioBase):
    def __init__(self, name: str = None):
        super().__init__(name=name)

    def configure(self, config):
        self.name = config.get("name")
        self.file = config.get("file")
        self.variables = config.get("variables", {})
        self.destination_nodes = self.variables.get("destination_nodes")
        self.destination_vm_id_start = self.variables.get("destination_vm_id_start")
        self.destination_vm_id_increment = self.variables.get(
            "destination_vm_id_increment"
        )
        self.network = self.variables.get("network", {})
        self.replications = self.variables.get("replications", {})
        self.ha = self.variables.get("ha", {})

    def run(self, proxmox_tasks: ProxmoxTasksAsync, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def pattern_increment(value, delta):
        # Find where the numeric part starts using a regular expression
        match = re.search(r"(\d+)", value)
        if match:
            start, end = match.start(), match.end()
            prefix = value[:start]  # Non-numeric prefix
            number = int(value[start:end])  # Numeric part
            suffix = value[end:]  # Any suffix after the number
            len_dig = end - start  # Length of the numeric part
            num_result = number + delta  # Incremented result
            # Reassemble with padding preserved
            return f"{prefix}{num_result:0{len_dig}d}{suffix}"
        return value

    @staticmethod
    def destination_nodes_pattern(input_str: str, value: str) -> str:
        # Match the content inside curly braces
        match = re.match(r"\{([^}]+)\}", input_str)
        if match:
            content = match.group(1)  # Extracts "destination_node|-1"
            parts = content.split("|")  # Split by "|"
            key = parts[0]  # "destination_node"
            delta = int(parts[1])  # -1 (converted to integer)
            if key == "destination_node":
                pattern_increment = SequenceScenariosBase.pattern_increment(
                    value, delta
                )
                print(f"Key: {key}, Delta: {delta}")
                return pattern_increment
        return input_str


if __name__ == "__main__":
    x1 = SequenceScenariosBase.destination_nodes_pattern("{destination_node|-1}", "c02")
    print(x1)

    x2 = SequenceScenariosBase.destination_nodes_pattern("{destination_node|+1}", "c02")
    print(x2)
