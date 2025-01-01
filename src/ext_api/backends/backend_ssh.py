import paramiko  # for Sync SSH
import asyncssh  # for Async SSH


from ext_api.backends.backend_cli import ProxmoxCLIBackend, ProxmoxAsyncCLIBackend


class ProxmoxSSHBackend(ProxmoxCLIBackend):
    def __init__(self, base_url: str, token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = base_url
        self.token = token

    def __enter__(self):
        # Setup CLI context (e.g., open SSH connection)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup CLI context (e.g., close SSH connection)
        pass

    def request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        **kwargs
    ):
        # Implement CLI command execution here
        return {"status": "success", "data": "Sync SSH result"}


class ProxmoxAsyncSSHBackend(ProxmoxAsyncCLIBackend):
    def __init__(self, base_url: str, token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = base_url
        self.token = token

    async def __aenter__(self):
        # Setup async SSH context
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup async SSH context
        pass

    async def async_request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        **kwargs
    ):
        # Implement async SSH command execution here
        return {"status": "success", "data": "Async SSH result"}
