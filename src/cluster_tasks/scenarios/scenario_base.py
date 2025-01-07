import logging
from abc import ABC, abstractmethod

from cluster_tasks.tasks.proxmox_tasks_base import ProxmoxTasksBase
from ext_api.proxmox_api import ProxmoxAPI
from cluster_tasks.tasks.proxmox_tasks_sync import ProxmoxTasksSync

logger = logging.getLogger("CT.{__name__}")


class ScenarioBase(ABC):
    def __init__(self, name: str = None):
        self.scenario_name = name or self.__class__.__name__

    @abstractmethod
    def run(self, node_tasks: ProxmoxTasksBase, *args, **kwargs):
        """Method to execute the scenario"""
        ...

    @abstractmethod
    def configure(self, config):
        """Method to configure the scenario"""
        ...
