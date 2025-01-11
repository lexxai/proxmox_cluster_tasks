
### ProxmoxAPI Class. Examples. 
The `ProxmoxAPI` class provides a context-friendly interface to interact with Proxmox. It supports using both manually created backend instances or automatically created instances via `backend_name` and `backend_type` parameters. Defaults: `backend_name="https"`, `backend_type="sync"`.

#### Example: Registered Backends (`https` in `sync` Mode)
```python
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI

register_backends("https")
ext_api = ProxmoxAPI(backend_name="https", backend_type="sync")
with ext_api as api:
    print(api.version.get(filter_keys="version"))
    nodes = api.nodes.get(filter_keys="node")
    node = nodes[0]
    print(api.cluster.ha.groups.get())
    print(api.nodes(node).status.get(filter_keys=["kversion", "uptime"]))
    print(api.nodes(node).status.get(filter_keys="current-kernel.release"))
    api.cluster.ha.groups.create(data={"group": "test_group_name", "nodes": ",".join(nodes[:3])})
    print(api.cluster.ha.groups("test_group_name").get(filter_keys=["group", "nodes"]))
    api.cluster.ha.groups("test_group_name").delete()
```

#### Example: Registered Backends (`https` in `async` Mode)
```python
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI

async def async_main():
    register_backends("https")
    ext_api = ProxmoxAPI(backend_name="https", backend_type="async")
    async with ext_api as api:
        print(await api.version.get(filter_keys="version"))
        print(await api.cluster.ha.groups.get())

asyncio.run(async_main())
```

#### Example: Registered Backends (`ssh` in `sync` Mode)
```python
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI

register_backends("ssh")
ext_api = ProxmoxAPI(backend_name="ssh", backend_type="sync")
with ext_api as api:
    print(api.version.get(filter_keys="version"))
```

#### Example: Manually Created Backend (`https` in `sync` Mode)
```python
from ext_api.backends.backend_https import ProxmoxHTTPSBackend
from ext_api.proxmox_api import ProxmoxAPI

backend = ProxmoxHTTPSBackend(
    base_url="https://proxmox.local:8006",
    token="user@pam!user_api=XXXX-YYYY-.....",
    verify_ssl=False
)

ext_api = ProxmoxAPI(backend=backend, backend_name="https", backend_type="sync")
with ext_api as api:
    print(api.version.get(filter_keys="version"))
```

These examples provide flexibility for  API usage, allowing you to control request preparation and execution explicitly.

[README](../README.md)
