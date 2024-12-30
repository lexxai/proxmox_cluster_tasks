import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(f"CT.{__name__}")


class Backend(ABC):
    def __init__(self):
        super().__init__()

    def close(self): ...

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return True

    @abstractmethod
    def process(self, input_data: dict | None = None) -> dict: ...


class AsyncBackend(ABC):

    def __init__(self):
        super().__init__()

    async def aclose(self): ...

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return True

    @abstractmethod
    async def aprocess(self, input_data: dict | None = None) -> dict: ...
