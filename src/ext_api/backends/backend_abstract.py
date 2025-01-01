from abc import ABC, abstractmethod


class ProxmoxBackend(ABC):
    def __init__(self, *args, **kwargs): ...

    def request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        *args,
        **kwargs
    ) -> dict:
        """Perform a synchronous API request."""
        raise NotImplementedError("Sync request not implemented for this backend")

    async def async_request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        *args,
        **kwargs
    ) -> dict:
        """Perform an asynchronous API request."""
        raise NotImplementedError("Async request not implemented for this backend")
