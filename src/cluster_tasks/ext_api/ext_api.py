import asyncio

from cluster_tasks.backends.abstract_backends import (
    AbstractBackend,
    AbstractAsyncBackend,
    BackendAbstractHAGroups,
)
from cluster_tasks.backends.http_backend import (
    BackendHTTP,
    BackendAsyncHTTP,
)
from cluster_tasks.backends.http_ha_groups import (
    BackendHttpHAGroups,
    BackendAsyncHttpHAGroups,
)


class ExtApi:
    def __init__(self, backend: AbstractBackend = None):
        self._backend: AbstractBackend | None = backend
        self._ha_groups: BackendAbstractHAGroups | None = None

    @property
    def backend(self) -> AbstractBackend:
        if self._backend is None:
            self._backend = BackendHTTP()
        return self._backend

    @property
    def ha_groups(self) -> BackendAbstractHAGroups:
        if self._ha_groups is None:
            if isinstance(self.backend, BackendHTTP):
                self._ha_groups = BackendHttpHAGroups(self.backend)
            else:
                raise NotImplementedError(
                    f"No HA groups implementation for backend type {type(self.backend).__name__}. "
                    "Please extend the 'ha_groups' property to support this backend type."
                )

        return self._ha_groups

    def __enter__(self):
        self.backend.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.backend.close()
        return False


class ExtApiAsync:
    def __init__(self, backend: AbstractAsyncBackend = None):
        self._backend: AbstractAsyncBackend | None = backend
        self._ha_groups: BackendAbstractHAGroups | None = None

    @property
    def backend(self) -> AbstractAsyncBackend:
        if self._backend is None:
            self._backend = BackendAsyncHTTP()
        return self._backend

    @property
    def ha_groups(self) -> BackendAbstractHAGroups:
        if self._ha_groups is None:
            if isinstance(self.backend, BackendAsyncHTTP):
                self._ha_groups = BackendAsyncHttpHAGroups(self.backend)
            else:
                raise NotImplementedError(
                    f"No HA groups implementation for backend type {type(self.backend).__name__}. "
                    "Please extend the 'ha_groups' property to support this backend type."
                )

        return self._ha_groups

    async def __aenter__(self):
        await self.backend.aconnect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.backend.aclose()
        return False


# Usage Example
if __name__ == "__main__":
    backend = BackendHTTP()
    with ExtApi(backend) as api:
        print(api.ha_groups.get())

    async def async_main():
        backend = BackendAsyncHTTP()
        async with ExtApiAsync(backend) as api:
            print(await api.ha_groups.get())

    asyncio.run(async_main())
