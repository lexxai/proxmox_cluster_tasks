import asyncio
import logging
from pyexpat.errors import messages

from cluster_tasks.backends.abstract_backends import (
    AbstractBackend,
    AbstractAsyncBackend,
    BackendAbstractHAGroups,
    BackendAbstractEndpoints,
)
from cluster_tasks.backends.http_backend import (
    BackendHTTP,
    BackendAsyncHTTP,
)
from cluster_tasks.backends.http_ha_groups import (
    BackendHttpHAGroups,
    BackendAsyncHttpHAGroups,
)
from cluster_tasks.config import configuration

logger = logging.getLogger(f"CT.{__name__}")


class AbstractExtApi:
    _class_mapping: dict[
        str, dict[type[AbstractBackend], type[BackendAbstractEndpoints]]
    ] = {"ha_groups": {AbstractBackend: BackendAbstractEndpoints}}

    def __init__(self, backend: AbstractBackend = None):
        self._backend: AbstractBackend | None = backend
        self._ha_groups: BackendAbstractHAGroups | None = None
        self.default_backend_class = AbstractBackend

    @property
    def backend(self) -> AbstractBackend:
        if self._backend is None:
            self._backend = self.default_backend_class()
        return self._backend

    @property
    def ha_groups(self) -> BackendAbstractHAGroups:
        if self._ha_groups is None:
            self._ha_groups = self.get_mapping("ha_groups")
        return self._ha_groups

    def get_mapping(self, entry_backend: str) -> BackendAbstractEndpoints:
        group_cls: type[BackendAbstractEndpoints] = self._class_mapping.get(
            entry_backend, {}
        ).get(type(self._backend))
        if group_cls is None:
            message = (
                f"No class implementation for backend type {type(self.backend).__name__}. "
                f"Please extend the '{entry_backend}' property to support this backend type."
            )
            logger.error(message)
            raise NotImplementedError(message)
        logger.debug(f"Mapping {entry_backend} to {group_cls.__name__}")
        return group_cls(self._backend)


class ExtApi(AbstractExtApi):
    _class_mapping = {
        "ha_groups": {
            BackendHTTP: BackendHttpHAGroups,
        }
    }

    def __init__(self, backend: AbstractBackend = None):
        super().__init__(backend=backend)
        self.default_backend_class = BackendHTTP

    def __enter__(self):
        self.backend.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.backend.close()
        return False


class ExtApiAsync(AbstractExtApi):
    _class_mapping = {
        "ha_groups": {
            BackendAsyncHTTP: BackendAsyncHttpHAGroups,
        }
    }

    def __init__(self, backend: AbstractAsyncBackend = None):
        super().__init__(backend=backend)
        self.default_backend_class = BackendAsyncHTTP

    async def __aenter__(self):
        await self.backend.aconnect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.backend.aclose()
        return False


# Usage Example
if __name__ == "__main__":
    logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
    logger.addHandler(logging.StreamHandler())

    backend = BackendHTTP()
    with ExtApi(backend) as api:
        print(api.ha_groups.get())

    async def async_main():
        backend = BackendAsyncHTTP()
        async with ExtApiAsync(backend) as api:
            print(await api.ha_groups.get())

    asyncio.run(async_main())
