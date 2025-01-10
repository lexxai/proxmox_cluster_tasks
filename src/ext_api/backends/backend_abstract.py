from abc import ABC, abstractmethod


class ProxmoxBackend(ABC):
    def __init__(self, *args, **kwargs): ...

    def connect(self, *args, **kwargs):
        raise NotImplementedError("Connect not implemented for this backend")

    def request(self, *args, **kwargs) -> dict:
        """Perform a synchronous API request."""
        raise NotImplementedError("Sync request not implemented for this backend")
        # return {"response": {"data": {}}, "status_code": 0, "success": True}

    async def async_request(self, *args, **kwargs) -> dict:
        """Perform an asynchronous API request."""
        raise NotImplementedError("Async request not implemented for this backend")
        # return {"response": {"data": {}}, "status_code": 0, "success": True}
