import logging

from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI

logger = logging.getLogger(f"CT.{__name__}")


class ProxmoxAPISim(ProxmoxAPI):
    METHODS = ["get", "post", "put", "delete"]
    METHOD_MAP = {"create": "post", "set": "put"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._path = []

    def __getattr__(self, name):
        if name.startswith("_") or (name in ["shape", "request", "async_request"]):
            # Ignore private methods
            return self
            # return super().__getattr__(name)
        # Append the accessed attribute to the path and return self for chaining
        self._path.append(name)
        return self

    def __call__(self, *args, **kwargs):
        if args:
            # If called with positional arguments, assume they are path parameters
            self._path.extend(args)
            return self
        # If called with keyword arguments, assume it's an action like GET, POST, etc.
        return self._execute(kwargs)
        # return self

    async def __acall__(self, *args, **kwargs):
        if args:
            # If called with positional arguments, assume they are path parameters
            self._path.extend(args)
        # If called with keyword arguments, assume it's an action like GET, POST, etc.
        if kwargs:
            return await self._async_execute(kwargs)
        return self

    def _execute(self, data):
        # Extract the action (last part of the path)
        action = self._path.pop()
        endpoint = "/".join(self._path)
        self._path = []  # Clear the path after generating the URL
        method = self.METHOD_MAP.get(action, action)
        if method not in self.METHODS:
            raise ValueError(f"Unsupported action: {action}")
        response = self.request(method=action, endpoint=endpoint, data=data)
        if response is not None and response.get("success"):
            response = response.get("response", {})
            if response:
                return response.get("data")
            else:
                logger.error(f"Failed to execute {action} on /{endpoint}: {response=}")
        else:
            logger.error(f"Failed to execute {action} on /{endpoint}: {response}")
        return None


if __name__ == "__main__":
    # Example usage
    register_backends()
    API = ProxmoxAPISim(backend_name="cli")
    with API as api:
        # Simulate API calls
        response1 = api.nodes("c01").status.get()
        # response2 = api.cluster.ha.groups.create(name="gr01", nodes="c01,c02:100")

        print(response1)
        # print(response2)
