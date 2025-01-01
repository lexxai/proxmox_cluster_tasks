import logging

from ext_api.backends.backend_registry import (
    BackendRegistry,
    BackendType,
)

logger = logging.getLogger(f"CT.{__name__}")

BACKENDS_NAMES = ["https", "cli", "ssh"]


def register_backends(names: list[str] | str = None):
    if names is None:
        names = BACKENDS_NAMES
    if isinstance(names, str):
        names = [names]
    for name in names:
        match name.strip().lower():
            case "https":
                try:
                    from ext_api.backends.backend_https import (
                        ProxmoxHTTPSBackend,
                        ProxmoxAsyncHTTPSBackend,
                    )

                    BackendRegistry.register_backend(
                        "https", BackendType.SYNC, ProxmoxHTTPSBackend
                    )
                    BackendRegistry.register_backend(
                        "https", BackendType.ASYNC, ProxmoxAsyncHTTPSBackend
                    )
                except ImportError:
                    logger.error("Failed to import HTTPS Backend")
            case "cli":
                try:
                    from ext_api.backends.backend_cli import (
                        ProxmoxCLIBackend,
                        ProxmoxAsyncCLIBackend,
                    )

                    BackendRegistry.register_backend(
                        "cli", BackendType.SYNC, ProxmoxCLIBackend
                    )
                    BackendRegistry.register_backend(
                        "cli", BackendType.ASYNC, ProxmoxAsyncCLIBackend
                    )
                except ImportError:
                    logger.error("Failed to import CLI Backend")
            case "ssh":
                try:
                    from ext_api.backends.backend_ssh import (
                        ProxmoxSSHBackend,
                        ProxmoxAsyncSSHBackend,
                    )

                    BackendRegistry.register_backend(
                        "ssh", BackendType.SYNC, ProxmoxSSHBackend
                    )
                    BackendRegistry.register_backend(
                        "ssh", BackendType.ASYNC, ProxmoxAsyncSSHBackend
                    )
                except ImportError:
                    logger.error("Failed to import SSH Backend")
            case _:
                logger.error(f"Unknown backend: {name}")


def get_backends_names():
    return list({key.name for key in BackendRegistry.registered_backends.keys()})


if __name__ == "__main__":
    register_backends(["https", "cli"])
    print(get_backends_names())
