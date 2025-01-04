import asyncio
import logging
import time
from abc import ABC, abstractmethod

from ext_api.proxmox_api import ProxmoxAPI

logger = logging.getLogger("CT.{__name__}")


class ScenarioBase(ABC):
    def __init__(self, api: ProxmoxAPI):
        self.name = self.__class__.__name__
        self.api: ProxmoxAPI = api

    @staticmethod
    def get_status(api: ProxmoxAPI, node: str, upid: str):
        result = api.nodes(node).tasks(upid).status.get(filter_keys="status")
        return result

    def wait_task_done(self, api: ProxmoxAPI, node: str, upid: str):
        while self.get_status(api, node, upid) != "stopped":
            logger.info("Waiting for task to finish...")
            time.sleep(2)

    @staticmethod
    async def async_get_status(api: ProxmoxAPI, node: str, upid: str):
        result = await api.nodes(node).tasks(upid).status.get(filter_keys="status")
        return result

    async def async_wait_task_done(self, api: ProxmoxAPI, node: str, upid: str):
        while await self.async_get_status(api, node, upid) != "stopped":
            logger.info("Waiting for task to finish...")
            await asyncio.sleep(2)

    @abstractmethod
    def run(self):
        """Method to execute the scenario"""
        ...

    @abstractmethod
    def configure(self, config):
        """Method to configure the scenario"""
        ...
