import logging

from ext_api.backends.backend_abstract import ProxmoxBackend

import httpx


logger = logging.getLogger("CT.{__name__}")


class ProxmoxHTTPBaseBackend(ProxmoxBackend):
    def __init__(self, base_url: str, entry_point: str, token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = base_url
        self.entry_point = entry_point.strip("/")
        self.token = token
        self._client: httpx.Client | httpx.AsyncClient | None = None

    def build_headers(self, token: str | None = None):
        headers = {
            "Authorization": f"PVEAPIToken={token or self.token}",
            "Content-Type": "application/url-encoded",
        }
        return headers

    def format_url(self, endpoint: str, params: dict = None) -> str:
        """Format the full URL for a given endpoint."""
        endpoint = endpoint.strip("/")
        if params:
            endpoint = endpoint.format(**params)
        return f"{self.base_url}/{self.entry_point}/{endpoint.lstrip('/')}"


class ProxmoxHTTPSBackend(ProxmoxHTTPBaseBackend):

    def connect(self):
        self._client = httpx.Client(headers=self.build_headers(), http2=True)

    def close(self):
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        """Initialize the HTTP session for synchronous usage."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the HTTP session for synchronous usage."""
        self.close()
        return True

    def request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        *args,
        **kwargs,
    ):
        """Make a synchronous HTTP request."""
        one_time = False
        if not self._client:
            self.connect()
            logger.warning(
                "HTTP client session is not initialized. Use 'with' context to start a session. Creating client in runtime"
            )
            one_time = True
        try:
            url = self.format_url(endpoint, params)
            response = self._client.request(method, url, data=data)
            response.raise_for_status()
            return response.json()
        finally:
            if one_time:
                self.close()


class ProxmoxAsyncHTTPSBackend(ProxmoxHTTPBaseBackend):

    async def connect(self):
        self._client = httpx.AsyncClient(headers=self.build_headers(), http2=True)

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """Initialize the HTTP session for asynchronous usage."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the HTTP session for asynchronous usage."""
        await self.close()
        return True

    async def async_request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        *args,
        **kwargs,
    ):
        """Make an asynchronous HTTP request."""
        one_time = False
        if not self._client:
            await self.connect()
            logger.warning(
                "HTTP client session is not initialized. Use 'with' context to start a session. Creating client in runtime"
            )
            one_time = True
        try:
            url = self.format_url(endpoint)
            response = await self._client.request(method, url, data=data)
            response.raise_for_status()
            return response.json()
        finally:
            if one_time:
                await self.close()
