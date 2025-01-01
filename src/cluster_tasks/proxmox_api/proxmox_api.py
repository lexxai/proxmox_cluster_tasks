from cluster_tasks.proxmox_api.backends.backend_registry import BackendRegistry
from cluster_tasks.proxmox_api.backends.registry import register_backends


class ProxmoxAPI:
    def __init__(
        self,
        base_url: str,
        token: str,
        backend_type: str = "sync",
        backend_name: str = "https",
    ):
        self.base_url = base_url
        self.token = token
        self.backend_type = backend_type.lower()
        self.backend_name = backend_name.lower()

        # Verify backend_name is registered
        self._backend = self._create_backend()

    def _create_backend(self):
        """Factory method to create the appropriate backend."""
        backend_cls = BackendRegistry.get_backend(self.backend_name, self.backend_type)
        if backend_cls:
            return backend_cls(self.base_url, self.token, self.backend_type)
        raise ValueError(f"Unsupported backend: {self.backend_name}")

    def __enter__(self):
        """Enter context for synchronous backends."""
        if self.backend_type != "sync":
            raise RuntimeError("Use 'async with' for asynchronous backends.")
        self._backend.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context for synchronous backends."""
        if self.backend_type == "sync":
            self._backend.__exit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self):
        """Enter context for asynchronous backends."""
        if self.backend_type != "async":
            raise RuntimeError("Use 'with' for synchronous backends.")
        await self._backend.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context for asynchronous backends."""
        if self.backend_type == "async":
            await self._backend.__aexit__(exc_type, exc_val, exc_tb)

    def request(
        self, method: str, endpoint: str, params: dict = None, data: dict = None
    ):
        """Make a synchronous request."""
        if self.backend_type != "sync":
            raise RuntimeError("This instance is configured for asynchronous requests.")
        return self._backend.request(method, endpoint, params, data)

    async def async_request(
        self, method: str, endpoint: str, params: dict = None, data: dict = None
    ):
        """Make an asynchronous request."""
        if self.backend_type != "async":
            raise RuntimeError("This instance is configured for synchronous requests.")
        return await self._backend.async_request(method, endpoint, params, data)


class ProxmoxSSHBackend:
    pass


if __name__ == "__main__":
    # Register backend with the registry
    register_backends()

    # Now you can use ProxmoxAPI with the backend you registered
    api = ProxmoxAPI(
        base_url="https://proxmox.local",
        token="your_token",
        backend_type="sync",
        backend_name="https",
    )

    with api as proxmox:
        response = proxmox.request("GET", "nodes/{node}", params={"node": "my_node"})
        print(response)
