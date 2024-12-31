import asyncio

from cluster_tasks.backends.http_backend import (
    BackendHTTP,
    BackendAsyncHTTP,
)
from cluster_tasks.backends.http_ha_groups import (
    BackendHttpHAGroups,
    BackendAsyncHttpHAGroups,
)


class API_HttpBackend:
    def __init__(self, backend=None):
        self.backend = backend or BackendHTTP()
        self.ha_groups = BackendHttpHAGroups(self.backend)

    def __enter__(self):
        self.backend.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.backend.close()
        return False


class API_AsyncHttpBackend:
    def __init__(self, backend=None):
        self.backend = backend or BackendAsyncHTTP()
        self.ha_groups = BackendAsyncHttpHAGroups(self.backend)

    async def __aenter__(self):
        await self.backend.aconnect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.backend.aclose()
        return False


if __name__ == "__main__":
    with API_HttpBackend() as api:
        print(api.ha_groups.get())

    async def async_main():
        async with API_AsyncHttpBackend() as api:
            print(await api.ha_groups.get())

    asyncio.run(async_main())
