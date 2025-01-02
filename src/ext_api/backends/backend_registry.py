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
    def unregister_backend(cls, name: str, backend_type: BackendType):
        """Unregister a backend class."""
        key = BackendKey(name, backend_type)
        del cls.registered_backends[key]


    @classmethod
    def get_backend(
        cls, name: str, backend_type: BackendType = BackendType.SYNC
    ) -> Type[T]:
        """Retrieve a registered backend class by name."""
        key = BackendKey(name, backend_type)
        return cls.registered_backends.get(key)

    @classmethod
    def get_backends_names(cls):
        return list({key.name for key in cls.registered_backends.keys()})

    @classmethod
    def get_backends_types(cls):
        return list({key.backend_type for key in cls.registered_backends.keys()})

    @classmethod
    def get_backends(cls):
        return cls.registered_backends

    @classmethod
    def clear(cls):
        cls.registered_backends.clear()

    @classmethod
    def get_name_type(cls, backend) -> tuple[str, BackendType] | tuple[None, None]:
        for key, value in cls.registered_backends.items():
            if isinstance(backend, value):
                return (key.name, key.backend_type)
        return None, None
