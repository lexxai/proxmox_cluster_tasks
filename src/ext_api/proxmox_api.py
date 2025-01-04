import asyncio
import logging
import threading
from typing import Self

from cluster_tasks.configure_logging import config_logger
from config.config import configuration
from ext_api.backends.registry import register_backends
from ext_api.proxmox_base_api import ProxmoxBaseAPI

logger = logging.getLogger(f"CT.{__name__}")


class ProxmoxAPI(ProxmoxBaseAPI):
    METHODS = ["get", "post", "put", "delete"]
    METHOD_MAP = {"create": "post", "set": "put"}
    _PRIVATE_METHODS = ["shape", "request", "async_request"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context_path = {}
        self._lock = threading.Lock()

    @staticmethod
    def _get_task_id() -> tuple[int, bool]:
        try:
            task = asyncio.current_task()
            task_id = id(task)
            logger.debug(f"ASYNC task_id: {task_id}")
            return task_id, True
        except RuntimeError:
            task_id = threading.get_ident()
            logger.debug(f"SYNC task_id: {task_id}")
            return task_id, False

    def _cleanup(self, task_id: int, is_async: bool = None):
        """Callback to clean up context when a task finishes."""
        # task_id = id(task)
        if is_async:
            self._context_path.pop(task_id, None)
        else:
            with self._lock:
                self._context_path.pop(task_id, None)

    def __getattr__(self, name) -> Self:
        if name.startswith("_") or (name in self._PRIVATE_METHODS):
            # Ignore private methods
            return self
        task_id, is_async = self._get_task_id()
        if is_async:
            if task_id not in self._context_path:
                self._context_path[task_id] = []
            self._context_path[task_id].append(name)
        else:
            with self._lock:
                if task_id not in self._context_path:
                    self._context_path[task_id] = []
                self._context_path[task_id].append(name)
        return self

    def __call__(self, *args, **kwargs):
        try:
            if asyncio.get_running_loop().is_running():
                return self.__acall__(*args, **kwargs)
        except RuntimeError:
            ...
        task_id, is_async = self._get_task_id()
        if args and not kwargs:
            with self._lock:
                self._context_path[task_id].extend(args)
            return self
        if kwargs.get("get_request_param"):
            kwargs.pop("get_request_param")
            return self._request_prepare(*args, **kwargs)
        result = self._execute(*args, **kwargs)
        # self._cleanup(task_id, is_async)
        return result

    def __acall__(self, *args, **kwargs):
        task_id, is_async = self._get_task_id()
        if args and not kwargs:
            self._context_path[task_id].extend(args)
        if kwargs.get("get_request_param"):
            kwargs.pop("get_request_param")
            return self._request_prepare(*args, **kwargs)
        result = self._async_execute(*args, **kwargs)
        # self._cleanup(task_id, is_async)
        return result

    def _request_prepare(self, data=None) -> dict:
        task_id, is_async = self._get_task_id()
        if is_async:
            action = self._context_path[task_id].pop()
            endpoint = "/".join(self._context_path[task_id])
            self._context_path[task_id] = (
                []
            )  # Clear the path after generating the endpoint
            self._cleanup(task_id, is_async)
        else:
            with self._lock:
                action = self._context_path[task_id].pop()
                endpoint = "/".join(self._context_path[task_id])
                self._context_path[task_id] = (
                    []
                )  # Clear the path after generating the endpoint
            self._cleanup(task_id, is_async)
        method = self.METHOD_MAP.get(action, action)
        if method not in self.METHODS:
            raise ValueError(f"Unsupported action: {action}")
        return {
            "method": method,
            "endpoint": endpoint,
            "data": data,
        }

    @staticmethod
    def _get_nested_value(data, key_path):
        """
        Helper function to fetch values from nested dictionaries or lists using a dotted key path.

        :param data: The dictionary or list to search through.
        :param key_path: The dotted key path (e.g., "kernel.cpu").
        :return: The value found at the specified key path, or None if not found.
        """
        keys = key_path.split(".")  # Split the dotted path into individual keys
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, None)
            elif isinstance(data, list) and key.isdigit():  # If key is an index
                try:
                    data = data[int(key)]
                except (ValueError, IndexError):
                    return None
            else:
                return None
            if data is None:
                return None
        return data

    def _filter_response(self, response_data, filter_keys=None):
        """
        Filters the response data based on the specified filter_keys, allowing for nested dotted keys.

        :param response_data: The data to filter (could be a list or dictionary).
        :param filter_keys: A string or list of strings specifying the keys to filter.
        :return: The filtered data.
        """
        if not filter_keys:
            return response_data

        if isinstance(response_data, list):
            if isinstance(filter_keys, str):
                response_data = [
                    self._get_nested_value(item, filter_keys) for item in response_data
                ]
            else:
                response_data = [
                    {
                        key: self._get_nested_value(item, key)
                        for key in filter_keys
                        if self._get_nested_value(item, key) is not None
                    }
                    for item in response_data
                ]
        elif isinstance(response_data, dict):
            if isinstance(filter_keys, str):
                response_data = self._get_nested_value(response_data, filter_keys)
            else:
                response_data = {
                    key: self._get_nested_value(response_data, key)
                    for key in filter_keys
                    if self._get_nested_value(response_data, key) is not None
                }

        return response_data

    def _response_analyze(self, response, filter_keys=None) -> str | list | dict | None:
        try:
            if response is None or not response.get("success"):
                raise Exception(response)
            response = response.get("response", {})
            if response is None:
                raise Exception(response)
            response_data = response.get("data")
            if response_data is None:
                return None
            return self._filter_response(response_data, filter_keys)
        except Exception as e:
            logger.error(f"Failed to execute: {e}")
            return None

    def _execute(
        self, data=None, filter_keys=None, params=None
    ) -> str | list | dict | None:
        params = params or self._request_prepare(data)
        response = self.request(**params)
        return self._response_analyze(response, filter_keys=filter_keys)

    async def _async_execute(
        self, data=None, filter_keys=None, params=None
    ) -> str | list | dict | None:
        params = params or self._request_prepare(data)
        response = await self.async_request(**params)
        return self._response_analyze(response, filter_keys=filter_keys)


if __name__ == "__main__":
    # Example usage
    logger = logging.getLogger("CT")
    logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
    config_logger(logger)
    register_backends()
    API = ProxmoxAPI(backend_name="https")
    with API as api:
        # Simulate API calls
        logger.info(api.version.get())
        # logger.info(sorted([n.get("id") for n in api.nodes.get()]))
        # logger.info(api.nodes.get(filter_keys=["node", "status"]))
        # logger.info(api.nodes.get())
        # logger.info(api.nodes("c01").status.get())
        # logger.info(api.cluster.ha.groups.create(name="test-gr02", nodes="c01,c02:100"))

        # print(response2)
