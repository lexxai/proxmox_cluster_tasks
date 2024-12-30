from abc import ABC, abstractmethod


class AbstractHandler(ABC):
    """Defines the contract for all handlers."""

    def __init__(self):
        super().__init__()

    def close(self): ...

    async def aclose(self): ...

    def __enter__(self):
        return self

    async def __aenter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return True

    async def __aexit__(self, exc_type, exc_value, traceback):
        return True

    @abstractmethod
    def process(self, input_data: dict | None = None) -> dict: ...

    @abstractmethod
    async def aprocess(self, input_data: dict | None = None) -> dict: ...

    @abstractmethod
    def get_version_data(self) -> dict:
        return {}

    def get_version(self) -> dict:
        return self.process(self.get_version_data())

    async def aget_version(self) -> dict:
        return await self.aprocess(self.get_version_data())

    @abstractmethod
    def get_ha_groups_data(self) -> dict:
        return {}

    def get_ha_groups(self):
        return self.process(self.get_ha_groups_data())

    async def aget_ha_groups(self):
        return await self.aprocess(self.get_ha_groups_data())

    @abstractmethod
    def get_status_data(self, target_node: str) -> dict:
        return {}

    def get_status(self, target_node: str) -> dict:
        return self.process(self.get_status_data(target_node))

    async def aget_status(self, target_node: str) -> dict:
        return await self.aprocess(self.get_status_data(target_node))
