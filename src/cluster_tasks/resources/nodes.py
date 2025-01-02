from ext_api.proxmox_api import ProxmoxAPI


class NodesResourcesBase:
    def __init__(self, ext_api: ProxmoxAPI):
        self.ext_api = ext_api
        self.node: str | None = None

    def __call__(self, node):
        self.node = node
        return self

    def _get_status_data(self, node: str = None):
        data = {
            "method": "get",
            "endpoint": "/nodes/{node}/status",
            "params": {"node": node or self.node},
        }
        return data


class NodesResources(NodesResourcesBase):
    def get_status(self, node: str = None):
        return self.ext_api.request(**self._get_status_data(node))


class NodesAsyncResources(NodesResourcesBase):
    async def get_status(self, node: str = None):
        return await self.ext_api.async_request(**self._get_status_data(node))
