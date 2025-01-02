from cluster_tasks.tasks.cluster_ha import (
    ClusterHaTasksBase,
    ClusterHaTasks,
    ClusterHaAsyncTasks,
)
from ext_api.proxmox_api import ProxmoxAPI


class ClusterTasksBase:
    def __init__(self, ext_api: ProxmoxAPI):
        self.ext_api = ext_api

    def _get_data(self):
        data = {
            "method": "get",
            "endpoint": "",
        }
        return data


class ClusterTasks(ClusterTasksBase):
    def __init__(self, ext_api):
        super().__init__(ext_api)
        self._ha: ClusterHaTasks | None = None

    @property
    def ha(self) -> ClusterHaTasks:
        if self._ha is None:
            self._ha = ClusterHaTasks(self.ext_api)
        return self._ha


class ClusterAsyncTasks(ClusterTasksBase):
    def __init__(self, ext_api):
        super().__init__(ext_api)
        self._ha: ClusterHaAsyncTasks | None = None

    @property
    def ha(self) -> ClusterHaAsyncTasks:
        if self._ha is None:
            self._ha = ClusterHaAsyncTasks(self.ext_api)
        return self._ha
