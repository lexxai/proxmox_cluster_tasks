from abc import ABC, abstractmethod


class AbstractHandler(ABC):
    """Defines the contract for all handlers."""

    @abstractmethod
    def process(self, input_data: dict | None = None):
        """Process the input data."""
        ...

    @abstractmethod
    def get_version(self) -> str: ...
