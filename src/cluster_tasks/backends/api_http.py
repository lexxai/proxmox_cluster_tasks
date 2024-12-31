import asyncio

from cluster_tasks.backends.backends import AbstractBackend, AbstractAsyncBackend
from cluster_tasks.backends.http_backend import (
    BackendHTTP,
    BackendAsyncHTTP,
)
from cluster_tasks.backends.http_ha_groups import (
    BackendHttpHAGroups,
    BackendAsyncHttpHAGroups,
)


class API:
    def __init__(self, backend: AbstractBackend = None):
        self._backend = backend
        self.ha_groups = BackendHttpHAGroups(self.backend)

    @property
    def backend(self):
        if self._backend is None:
            self._backend = BackendHTTP()
        return self._backend

    def __enter__(self):
        self.backend.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.backend.close()
        return False


class API_Async:
    def __init__(self, backend: AbstractAsyncBackend = None):
        self._backend = backend
        self.ha_groups = BackendAsyncHttpHAGroups(self.backend)

    @property
    def backend(self):
        if self._backend is None:
            self._backend = BackendAsyncHTTP()
        return self._backend

    async def __aenter__(self):
        await self.backend.aconnect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.backend.aclose()
        return False


if __name__ == "__main__":
    backend = BackendHTTP()
    with API(backend) as api:
        print(api.ha_groups.get())

    async def async_main():
        backend = BackendAsyncHTTP()
        async with API_Async(backend) as api:
            print(await api.ha_groups.get())

    asyncio.run(async_main())
