from ext_api.proxmox_api import ProxmoxAPI


class TemplateResourcesBase:
    def __init__(self, ext_api: ProxmoxAPI):
        self.ext_api = ext_api

    def _get_data(self):
        data = {
            "method": "get",
            "endpoint": "",
        }
        return data


class TemplateResources(TemplateResourcesBase): ...


class TemplateAsyncResources(TemplateResourcesBase): ...
