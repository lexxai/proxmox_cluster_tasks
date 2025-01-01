from abc import ABC, abstractmethod


class ProxmoxBackend(ABC):
    @abstractmethod
    def request(
        self, method: str, endpoint: str, params: dict = None, data: dict = None
    ) -> dict:
        """Perform a synchronous API request."""
        ...

    async def async_request(
        self, method: str, endpoint: str, params: dict = None, data: dict = None
    ) -> dict:
        """Perform an asynchronous API request."""
        raise NotImplementedError("Async request not implemented for this backend")
