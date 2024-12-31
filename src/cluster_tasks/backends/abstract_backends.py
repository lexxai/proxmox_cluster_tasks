import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(f"CT.{__name__}")


class AbstractBackend(ABC):
    def __init__(self):
        super().__init__()
        self.entry_points: dict = {}

    def connect(self, *args, **kwargs): ...

    def close(self): ...

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return True

    @abstractmethod
    def process(self, input_data: dict | None = None) -> dict: ...


#
#
class AbstractAsyncBackend(ABC):

    def __init__(self):
        super().__init__()

    async def aconnect(self, *args, **kwargs): ...

    async def aclose(self): ...

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return True

    @abstractmethod
    async def aprocess(self, input_data: dict | None = None) -> dict: ...


class BackendAbstractEndpoints(ABC):
    def __init__(self, backend: AbstractBackend = None):
        super().__init__()
        self.backend = backend


class BackendAbstractHAGroups(BackendAbstractEndpoints):
    @abstractmethod
    def get(self): ...

    @abstractmethod
    def create(
        self,
        name: str,
        nodes: list[str],
        comment: str = None,
        nofailback: bool = None,
        restricted: bool = None,
    ): ...
