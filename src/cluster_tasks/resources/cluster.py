from cluster_tasks.resources.cluster_ha import (
    ClusterHaResourcesBase,
    ClusterHaResources,
    ClusterHaAsyncResources,
)
from ext_api.proxmox_api import ProxmoxAPI


class ClusterResourcesBase:
    def __init__(self, ext_api: ProxmoxAPI):
        self.ext_api = ext_api

    def _get_data(self):
        data = {
            "method": "get",
            "endpoint": "",
        }
        return data


class ClusterResources(ClusterResourcesBase):
    def __init__(self, ext_api):
        super().__init__(ext_api)
        self._ha: ClusterHaResources | None = None

    @property
    def ha(self) -> ClusterHaResources:
        if self._ha is None:
            self._ha = ClusterHaResources(self.ext_api)
        return self._ha


class ClusterAsyncResources(ClusterResourcesBase):
    def __init__(self, ext_api):
        super().__init__(ext_api)
        self._ha: ClusterHaAsyncResources | None = None

    @property
    def ha(self) -> ClusterHaAsyncResources:
        if self._ha is None:
            self._ha = ClusterHaAsyncResources(self.ext_api)
        return self._ha
