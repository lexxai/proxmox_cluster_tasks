from ext_api.proxmox_api import ProxmoxAPI


class ClusterHaResourcesBase:
    def __init__(self, ext_api: ProxmoxAPI):
        self.ext_api = ext_api

    def _get_groups_data(self):
        data = {
            "method": "get",
            "endpoint": "/cluster/ha/groups",
        }
        return data


class ClusterHaResources(ClusterHaResourcesBase):
    def get_groups(self):
        return self.ext_api.request(**self._get_groups_data())


class ClusterHaAsyncResources(ClusterHaResourcesBase):
    async def get_groups(self):
        return await self.ext_api.async_request(**self._get_groups_data())