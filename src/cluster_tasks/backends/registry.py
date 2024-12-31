import logging
from typing import Type, Dict

logger = logging.getLogger(f"CT.{__name__}")


class BackendRegistry:
    registry: Dict[str, Dict[Type, Type]] = {}

    @classmethod
    def register(
        cls, entry_backend: str, backend_type: Type, implementation_type: Type
    ):
        if entry_backend not in cls.registry:
            cls.registry[entry_backend] = {}
        cls.registry[entry_backend][backend_type] = implementation_type

    @classmethod
    def get(cls, entry_backend: str, backend_type: Type):
        entry_registry = cls.registry.get(entry_backend)
        if entry_registry is None or backend_type not in entry_registry:
            message = (
                f"No class implementation for backend type {backend_type.__name__}. "
                f"Please extend the '{entry_backend}' property to support this backend type."
            )
            # logger.error(message)
            raise NotImplementedError(message)
        return entry_registry[backend_type]
