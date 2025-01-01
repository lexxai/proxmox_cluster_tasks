from ext_api.backends.backend_registry import (
    BackendRegistry,
    BackendType,
)
from ext_api.backends.backend_cli import ProxmoxCLIBackend, ProxmoxAsyncCLIBackend
from ext_api.backends.backend_https import ProxmoxHTTPSBackend, ProxmoxAsyncHTTPSBackend
from ext_api.backends.backend_ssh import (
    ProxmoxSSHBackend,
    ProxmoxAsyncSSHBackend,
)


def register_backends():
    BackendRegistry.register_backend("https", BackendType.SYNC, ProxmoxHTTPSBackend)
    BackendRegistry.register_backend(
        "https", BackendType.ASYNC, ProxmoxAsyncHTTPSBackend
    )
    BackendRegistry.register_backend("cli", BackendType.SYNC, ProxmoxCLIBackend)
    BackendRegistry.register_backend("cli", BackendType.ASYNC, ProxmoxAsyncCLIBackend)
    BackendRegistry.register_backend("ssh", BackendType.SYNC, ProxmoxSSHBackend)
    BackendRegistry.register_backend("ssh", BackendType.ASYNC, ProxmoxAsyncSSHBackend)


def get_backends_names():
    return list({key.name for key in BackendRegistry.registered_backends.keys()})


if __name__ == "__main__":
    register_backends()
    print(get_backends_names())
