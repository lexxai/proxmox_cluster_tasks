from abc import ABC, abstractmethod


class ProxmoxBackend(ABC):
    def __init__(self, *args, **kwargs): ...

    def request(self, *args, **kwargs) -> dict:
        """Perform a synchronous API request."""
        raise NotImplementedError("Sync request not implemented for this backend")

    async def async_request(self, *args, **kwargs) -> dict:
        """Perform an asynchronous API request."""
        raise NotImplementedError("Async request not implemented for this backend")
