from cluster_tasks.proxmox_api.backends.abstract_backend import ProxmoxBackend


class ProxmoxHTTPSBackend(ProxmoxBackend):
    def __init__(self, base_url: str, token: str, backend_type: str):
        self.base_url = base_url
        self.token = token
        self.backend_type = backend_type

    def __enter__(self):
        # Open HTTPS session or perform necessary setup
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup HTTPS session
        ...

    def request(
        self, method: str, endpoint: str, params: dict = None, data: dict = None
    ):
        # Handle the synchronous HTTPS request
        return {"status": "success", "data": "Sync HTTPS result"}


class ProxmoxAsyncHTTPSBackend(ProxmoxBackend):
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

    async def __aenter__(self):
        # Setup async SSH context
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup async SSH context
        pass

    async def async_request(
        self, method: str, endpoint: str, params: dict = None, data: dict = None
    ):
        # Implement async SSH command execution here
        return {"status": "success", "data": "Async SSH result"}
