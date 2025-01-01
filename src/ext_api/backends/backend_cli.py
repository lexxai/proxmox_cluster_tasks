from ext_api.backends.backend_abstract import ProxmoxBackend


class ProxmoxCLIBackend(ProxmoxBackend):
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

    def __enter__(self):
        # Setup CLI context (e.g., open SSH connection)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup CLI context (e.g., close SSH connection)
        pass

    def request(
        self, method: str, endpoint: str, params: dict = None, data: dict = None
    ):
        # Implement CLI command execution here
        return {"status": "success", "data": "CLI result"}


class ProxmoxAsyncCLIBackend(ProxmoxBackend):
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
        return {"status": "success", "data": "Async CLI result"}
