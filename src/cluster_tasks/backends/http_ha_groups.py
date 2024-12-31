from abc import ABC, abstractmethod

from cluster_tasks.backends.abstract_backends import BackendAbstractHAGroups
from cluster_tasks.backends.http_backend import BackendHTTP, BackendAsyncHTTP
from cluster_tasks.backends.registry import BackendRegistry


class BackendAbstractHttpHAGroups(BackendAbstractHAGroups):

    def get_data(self) -> dict:
        input_data = {
            "entry_point": self.backend.entry_points.get("HA_GROUPS"),
            "method": "GET",
        }
        return input_data

    def create_data(
        self,
        name: str,
        nodes: list[str],
        comment: str = None,
        nofailback: bool = None,
        restricted: bool = None,
    ) -> dict:
        nodes = ",".join(nodes)
        input_data = {
            "entry_point": self.backend.entry_points.get("HA_GROUPS"),
            "method": "POST",
            "data": {"group": name, "nodes": nodes},
        }
        return input_data


class BackendHttpHAGroups(BackendAbstractHttpHAGroups):

    def get(self):
        return self.backend.process(self.get_data())

    def create(
        self,
        name: str,
        nodes: list[str],
        comment: str = None,
        nofailback: bool = None,
        restricted: bool = None,
    ):
        return self.backend.process(
            self.create_data(name, nodes, comment, nofailback, restricted)
        )


class BackendAsyncHttpHAGroups(BackendAbstractHttpHAGroups):

    async def get(self):
        return await self.backend.aprocess(self.get_data())

    async def create(
        self,
        name: str,
        nodes: list[str],
        comment: str = None,
        nofailback: bool = None,
        restricted: bool = None,
    ):
        return await self.backend.aprocess(
            self.create_data(name, nodes, comment, nofailback, restricted)
        )


# Register backend mappings
BackendRegistry.register("ha_groups", BackendHTTP, BackendHttpHAGroups)
BackendRegistry.register("ha_groups", BackendAsyncHTTP, BackendAsyncHttpHAGroups)
