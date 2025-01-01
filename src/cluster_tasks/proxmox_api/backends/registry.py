from cluster_tasks.proxmox_api.backends.backend_registry import BackendRegistry, BackendType
from cluster_tasks.proxmox_api.backends.backend_cli import ProxmoxCLIBackend
from cluster_tasks.proxmox_api.backends.backend_https import ProxmoxHTTPSBackend
from cluster_tasks.proxmox_api.proxmox_api import ProxmoxSSHBackend


def register_backends():
    BackendRegistry.register_backend("https", BackendType.SYNC, ProxmoxHTTPSBackend)
    BackendRegistry.register_backend("cli", BackendType.SYNC, ProxmoxCLIBackend)
    BackendRegistry.register_backend("ssh", BackendType.SYNC, ProxmoxSSHBackend)
    BackendRegistry.register_backend("https", BackendType.ASYNC, ProxmoxHTTPSBackend)
    BackendRegistry.register_backend("cli", BackendType.ASYNC, ProxmoxCLIBackend)
    BackendRegistry.register_backend("ssh", BackendType.ASYNC, ProxmoxSSHBackend)
