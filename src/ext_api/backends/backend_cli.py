import logging

from ext_api.backends.backend_abstract import ProxmoxBackend

logger = logging.getLogger("CT.{__name__}")


class ProxmoxCLIBaseBackend(ProxmoxBackend):
    def __init__(
        self,
        entry_point: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.entry_point = entry_point.strip("/")

    def format_url(self, endpoint: str, params: dict = None, method: str = None) -> str:
        """Format the full URL for a given endpoint."""
        endpoint = endpoint.strip("/")
        if params:
            endpoint = endpoint.format(**params)
        return f"{self.entry_point} {method.strip().lower()} {endpoint.lstrip('/')}"


class ProxmoxCLIBackend(ProxmoxCLIBaseBackend):

    def request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        *args,
        **kwargs,
    ):
        url = self.format_url(endpoint, params, method)

        # Implement CLI command execution here
        return {"url": url}


class ProxmoxAsyncCLIBackend(ProxmoxCLIBaseBackend):

    async def async_request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        *args,
        **kwargs,
    ):
        # Implement async SSH command execution here
        return {"status": "success", "data": "Async CLI result"}
