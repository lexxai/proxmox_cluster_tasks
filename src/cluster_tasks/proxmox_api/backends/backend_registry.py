from collections import namedtuple
from enum import StrEnum
from typing import TypeVar, Type

T = TypeVar("T", bound="ProxmoxBackend")

BackendKey = namedtuple("BackendKey", ["name", "backend_type"])


class BackendType(StrEnum):
    SYNC = "sync"
    ASYNC = "async"


class BackendRegistry:
    registered_backends: dict[BackendKey, Type[T]] = {}

    @classmethod
    def register_backend(
        cls, name: str, backend_type: BackendType, backend_cls: Type[T]
    ):
        """Register a backend class."""
        key = BackendKey(name, backend_type)
        cls.registered_backends[key] = backend_cls

    @classmethod
    def get_backend(
        cls, name: str, backend_type: BackendType = BackendType.SYNC
    ) -> Type[T]:
        """Retrieve a registered backend class by name."""
        key = BackendKey(name, backend_type)
        return cls.registered_backends.get(key)
