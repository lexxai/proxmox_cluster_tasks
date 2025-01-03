import logging

from cluster_tasks.configure_logging import config_logger
from config.config import configuration
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
        if args and not kwargs:
            self._path.extend(args)
            return self
        return self._execute(*args, **kwargs)

    async def __acall__(self, *args, **kwargs):
        if args and not kwargs:
            self._path.extend(args)
            return self
        return await self._aync_execute(*args, **kwargs)

    def _request_prepare(self, data=None, filter_keys=None):
        action = self._path.pop()
        endpoint = "/".join(self._path)
        self._path = []  # Clear the path after generating the URL
        logger.debug(f"Executing {action} on /{endpoint}: {data=}, {filter_keys=}")
        method = self.METHOD_MAP.get(action, action)
        if method not in self.METHODS:
            raise ValueError(f"Unsupported action: {action}")
        return {
            "method": method,
            "endpoint": endpoint,
            "data": data,
        }

    @staticmethod
    def _response_analyze(response, filter_keys=None):
        if response is not None and response.get("success"):
            response = response.get("response", {})
            if response:
                response_data = response.get("data")
                if filter_keys and isinstance(response_data, list):
                    if isinstance(filter_keys, str):
                        response_data = [
                            item.get(filter_keys) for item in response_data
                        ]
                    else:
                        response_data = [
                            {key: item.get(key) for key in filter_keys if key in item}
                            for item in response_data
                        ]
                    # logger.debug(f"Filtered data: {response_data=}")
                return response_data
            else:
                logger.error(f"Failed to execute: {response=}")
        else:
            logger.error(f"Failed to execute: {response}")
        return None

    def _execute(self, data=None, filter_keys=None):
        params = self._request_prepare(data, filter_keys=filter_keys)
        response = self.request(**params)
        return self._response_analyze(response, filter_keys=filter_keys)

    async def _async_execute(self, data=None, filter_keys=None):
        params = self._request_prepare(data, filter_keys=filter_keys)
        response = await self.request(**params)
        return self._response_analyze(response, filter_keys=filter_keys)


if __name__ == "__main__":
    # Example usage
    logger = logging.getLogger("CT")
    logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
    config_logger(logger)
    register_backends()
    API = ProxmoxAPISim(backend_name="https")
    with API as api:
        # Simulate API calls
        logger.info(sorted([n.get("id") for n in api.nodes.get()]))
        logger.info(api.nodes.get(filter_keys=["node", "status"]))
        logger.info(api.nodes.get())
        logger.info(api.nodes("c01").status.get())
        # logger.info(api.cluster.ha.groups.create(name="test-gr02", nodes="c01,c02:100"))

        # print(response2)
