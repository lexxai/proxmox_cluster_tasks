from cluster_tasks.tasks.cluster import (
    ClusterTasks,
    ClusterAsyncTasks,
)
from cluster_tasks.tasks.nodes import NodesTasks, NodesAsyncTasks
from ext_api.proxmox_api import ProxmoxAPI


class ProxmoxTasksBase:
    def __init__(self, ext_api: ProxmoxAPI):
        self.ext_api = ext_api

    def _get_version_data(self):
        data = {
            "method": "get",
            "endpoint": "version",
        }
        return data


class ProxmoxTasks(ProxmoxTasksBase):
    def __init__(self, ext_api: ProxmoxAPI):
        super().__init__(ext_api)
        self._cluster: ClusterTasks | None = None
        self._nodes: NodesTasks | None = None

    @property
    def cluster(self) -> ClusterTasks:
        if self._cluster is None:
            self._cluster = ClusterTasks(self.ext_api)
        return self._cluster

    @property
    def nodes(self) -> NodesTasks:
        if self._nodes is None:
            self._nodes = NodesTasks(self.ext_api)
        return self._nodes

    def get_version(self):
        return self.ext_api.request(**self._get_version_data())


class ProxmoxAsyncTasks(ProxmoxTasksBase):
    def __init__(self, ext_api: ProxmoxAPI):
        super().__init__(ext_api)
        self._cluster: ClusterAsyncTasks | None = None
        self._nodes: NodesAsyncTasks | None = None

    @property
    def cluster(self) -> ClusterAsyncTasks:
        if self._cluster is None:
            self._cluster = ClusterAsyncTasks(self.ext_api)
        return self._cluster

    @property
    def nodes(self) -> NodesAsyncTasks:
        if self._nodes is None:
            self._nodes = NodesAsyncTasks(self.ext_api)
        return self._nodes

    async def get_version(self):
        return await self.ext_api.async_request(**self._get_version_data())
