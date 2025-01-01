from typing import TypeVar, Type

T = TypeVar("T", bound="ProxmoxBackend")


class BackendRegistry:
    registered_backends: dict[str, Type[T]] = {}

    @classmethod
    def register_backend(cls, name: str, backend_cls: Type[T]):
        """Register a backend class."""
        cls.registered_backends[name] = backend_cls

    @classmethod
    def get_backend(cls, name: str) -> Type[T]:
        """Retrieve a registered backend class by name."""
        return cls.registered_backends.get(name)
