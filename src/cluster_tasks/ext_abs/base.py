from abc import ABC, abstractmethod


class AbstractHandler(ABC):
    """Defines the contract for all handlers."""

    def __init__(self):
        super().__init__()

    def __enter__(self):
        return self

    async def __aenter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return True

    async def __aexit__(self, exc_type, exc_value, traceback):
        return True

    def process(self, input_data: dict | None = None) -> dict:
        """Process the input data."""
        ...

    async def aprocess(self, input_data: dict | None = None) -> dict:
        """Process the input data."""
        ...

    @abstractmethod
    def get_version(self) -> dict: ...

    @abstractmethod
    async def aget_version(self) -> dict: ...
