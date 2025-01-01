from abc import ABC, abstractmethod


class ProxmoxBackend(ABC):
    def request(
        self, method: str, endpoint: str, params: dict = None, data: dict = None
    ) -> dict:
        """Perform a synchronous API request."""
        raise NotImplementedError("Sync request not implemented for this backend")

    async def async_request(
        self, method: str, endpoint: str, params: dict = None, data: dict = None
    ) -> dict:
        """Perform an asynchronous API request."""
        raise NotImplementedError("Async request not implemented for this backend")
