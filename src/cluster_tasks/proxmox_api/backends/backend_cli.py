from cluster_tasks.proxmox_api.backends.abstract_backend import ProxmoxBackend


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
