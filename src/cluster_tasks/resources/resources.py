from cluster_tasks.resources.cluster import (
    ClusterResources,
    ClusterAsyncResources,
)
from cluster_tasks.resources.config import api_resources
from cluster_tasks.resources.nodes import NodesResources, NodesAsyncResources
from ext_api.proxmox_api import ProxmoxAPI


class ResourcesBase:
    def __init__(self, ext_api: ProxmoxAPI):
        self.ext_api = ext_api
        self.resources = api_resources.get("ROOT", {})

    def _get_version_data(self):
        data = {
            "method": "get",
            "endpoint": self.resources.get("VERSION"),
        }
        return data


class Resources(ResourcesBase):
    def __init__(self, ext_api: ProxmoxAPI):
        super().__init__(ext_api)
        self._cluster: ClusterResources | None = None
        self._nodes: NodesResources | None = None

    @property
    def cluster(self) -> ClusterResources:
        if self._cluster is None:
            self._cluster = ClusterResources(self.ext_api)
        return self._cluster

    @property
    def nodes(self) -> NodesResources:
        if self._nodes is None:
            self._nodes = NodesResources(self.ext_api)
        return self._nodes

    def get_version(self):
        return self.ext_api.request(**self._get_version_data())


class AsyncResources(ResourcesBase):
    def __init__(self, ext_api: ProxmoxAPI):
        super().__init__(ext_api)
        self._cluster: ClusterAsyncResources | None = None
        self._nodes: NodesAsyncResources | None = None

    @property
    def cluster(self) -> ClusterAsyncResources:
        if self._cluster is None:
            self._cluster = ClusterAsyncResources(self.ext_api)
        return self._cluster

    @property
    def nodes(self) -> NodesAsyncResources:
        if self._nodes is None:
            self._nodes = NodesAsyncResources(self.ext_api)
        return self._nodes

    async def get_version(self):
        return await self.ext_api.async_request(**self._get_version_data())
