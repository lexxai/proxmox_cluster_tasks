import logging

logger = logging.getLogger("CT.{__name__}")

try:
    import httpx
except ImportError as e:
    logger.error(f"HTTPS Backend require load module: {e}")
    exit(1)

from ext_api.backends.backend_abstract import ProxmoxBackend


"""
Proxmox backends for http/https protocols.

This module contains the classes for backends that communicate with the Proxmox API using the
http/https protocols.

The ProxmoxHTTPBaseBackend class is a base class for the ProxmoxHTTPSBackend and ProxmoxHTTPBackend
classes. It contains the common methods for both classes.

The ProxmoxHTTPSBackend class is a backend that communicates with the Proxmox API using the
https protocol.

The ProxmoxHTTPBackend class is a backend that communicates with the Proxmox API using the
http protocol.
"""


class ProxmoxHTTPBaseBackend(ProxmoxBackend):
    def __init__(
        self,
        base_url: str,
        entry_point: str,
        token: str,
        verify_ssl: bool = True,
        *args,
        **kwargs,
    ):
        """
        Initialize a ProxmoxHTTPBaseBackend instance.
        Args:
            base_url (str): The base URL for the Proxmox API.
            entry_point (str): The entry point for the Proxmox API.
            token (str): The token used for authentication with the Proxmox API.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.base_url = base_url
        self.entry_point = entry_point.strip("/")
        self.token = token
        self.token_delimiter = "="
        self.verify_ssl = verify_ssl
        self._client: httpx.Client | httpx.AsyncClient | None = None

    def get_authorization(self, token: str | None = None):
        return f"PVEAPIToken{self.token_delimiter}{token or self.token}"

    def build_headers(self, token: str | None = None):
        headers = {
            "Authorization": self.get_authorization(token),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        return headers

    def format_url(self, endpoint: str, endpoint_params: dict = None) -> str:
        if not endpoint:
            raise ValueError("HTTPS backend: Endpoint is required")
        """Format the full URL for a given endpoint."""
        endpoint = endpoint.strip("/")
        if endpoint_params:
            endpoint = endpoint.format(**endpoint_params)
        logger.debug(f"Formatted endpoint: /{self.entry_point}/{endpoint}")
        return f"{self.base_url}/{self.entry_point}/{endpoint.lstrip('/')}"

    @staticmethod
    def response_analyze(response: httpx.Response):
        success = response.status_code < 400
        result = {
            "response": response.json() if success else {},
            "status_code": response.status_code,
            "success": success,
        }
        return result

    @property
    def client(self):
        return self._client


class ProxmoxHTTPSBackend(ProxmoxHTTPBaseBackend):
    """
    Initialize a ProxmoxHTTPSBackend instance.
    Args:
    base_url (str): The base URL for the Proxmox API.
    entry_point (str): The entry point for the Proxmox API.
    token (str): The token used for authentication with the Proxmox API.
    *args: Additional positional arguments.
    **kwargs: Additional keyword arguments.
    """

    def connect(self):
        # logger.debug(f"Connecting to Proxmox API... {self.verify_ssl=}")
        self._client = httpx.Client(
            headers=self.build_headers(), http2=True, verify=self.verify_ssl
        )

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
        endpoint_params: dict = None,
        *args,
        **kwargs,
    ):
        """Make a synchronous HTTP request."""
        one_time = False
        if not self._client:
            self.connect()
            logger.warning(
                "HTTP client session is not initialized. Use 'with' context to start a session. Creating onetime client instance."
            )
            one_time = True
        try:
            # logger.debug(f"Request: {method=}, {url=}, {data=}, {params=}")
            try:
                url = self.format_url(endpoint, endpoint_params)
                response = self._client.request(method, url, data=data, params=params)
                return self.response_analyze(response)
            except Exception as exc:
                return {
                    "response": {},
                    "status_code": 999,
                    "error": str(exc),
                    "success": False,
                }
        finally:
            if one_time:
                self.close()


class ProxmoxAsyncHTTPSBackend(ProxmoxHTTPBaseBackend):

    async def connect(self):
        self._client = httpx.AsyncClient(
            headers=self.build_headers(), http2=True, verify=self.verify_ssl
        )

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
        endpoint_params: dict = None,
        *args,
        **kwargs,
    ):
        """Make an asynchronous HTTP request."""
        one_time = False
        if not self._client:
            await self.connect()
            logger.warning(
                "HTTP client session is not initialized. Use 'with' context to start a session. Creating onetime client instance."
            )
            one_time = True
        try:
            try:
                url = self.format_url(endpoint, endpoint_params)
                # logger.debug(f"Request: {method=}, {url=}, {data=}, {params=}")
                response = await self._client.request(
                    method, url, data=data, params=params
                )
                return self.response_analyze(response)
            except Exception as exc:
                return {
                    "response": {},
                    "status_code": 999,
                    "error": str(exc),
                    "success": False,
                }

        finally:
            if one_time:
                await self.close()
