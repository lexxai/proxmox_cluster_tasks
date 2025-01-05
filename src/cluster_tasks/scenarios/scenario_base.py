import logging
from abc import ABC, abstractmethod

from ext_api.proxmox_api import ProxmoxAPI
from cluster_tasks.tasks.node_tasks_sync import NodeTasksSync

logger = logging.getLogger("CT.{__name__}")


class ScenarioBase(ABC):
    def __init__(self, api: ProxmoxAPI):
        self.name = self.__class__.__name__
        self.api: ProxmoxAPI = api
        self.node_tasks = NodeTasksSync(api)

    @abstractmethod
    def run(self):
        """Method to execute the scenario"""
        ...

    @abstractmethod
    def configure(self, config):
        """Method to configure the scenario"""
        ...
