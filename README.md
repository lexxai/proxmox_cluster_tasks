# proxmox_cluster_tasks
proxmox cluster automatic tasks helper

## API Reference
- Usage of Proxmox VE API : https://pve.proxmox.com/wiki/Proxmox_VE_API
- Proxmox VE API Viewer: https://pve.proxmox.com/pve-docs/api-viewer


## Setup
### Backends
Present some list of allowed backends:
```python
BACKENDS_NAMES = ["https", "cli", "ssh"]
```
#### Automatically register backends
For use backends you can register all backends or selected list only with default settings by use config file by use 
`register_backends()`:
```python
# register_backends()
# register_backends("https")
# register_backends(["https", "ssh"])
```
Backends registered as for sync code and for async code for use `asyncio` module.

#### Manually create instance of backend
Or you can create instance of backend class manually with manual import module of backand:
```python
from ext_api.backends.backend_https import (
    ProxmoxHTTPSBackend
)

backend = ProxmoxHTTPSBackend(
    base_url: str,
    entry_point: str,
    token: str,
    verify_ssl: bool = True)
```

### class ProxmoxAPI
Context friendly instance of ProxmoxAPI allow use manually created backed instance, or create instance inside of class automatically
For automatically create instance can use `backend_name` and `backend_type` by default used: `backend_name="https"`, `backend_type="sync"`
#### Registered backends "https" in "sync" mode
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
    api.cluster.ha.groups.create(
            data={"group": "test_group_name", "nodes": ",".join(nodes[:3])}
        )
    print(
        api.cluster.ha.groups("test_group_name").get(filter_keys=["group", "nodes"])
    )
    api.cluster.ha.groups("test_group_name").delete()
```

#### Registered backends "https" in "async" mode
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

#### Registered backends "ssh" in "sync" mode
```python    
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI

register_backends("ssh")
ext_api = ProxmoxAPI(backend_name="ssh", backend_type="sync")
with ext_api as api:
    print(api.version.get(filter_keys="version"))
```

#### Manually created backends "https" in "sync"
```python
from ext_api.backends.backend_https import (
    ProxmoxHTTPSBackend
)
from ext_api.proxmox_api import ProxmoxAPI

backend = ProxmoxHTTPSBackend(
    base_url = "https://proxmox.local:8006",
    token: "user@pam!user_api=XXXX-YYYY-.....",
    verify_ssl= False)

ext_api = ProxmoxAPI(backend=backend, backend_name="https", backend_type="sync")
with ext_api as api:
    print(api.version.get(filter_keys="version"))
```

#### Registered backends "https" in "async" mode multiple parallel instances
```python
async def async_main():
    register_backends("https")
    ext_api = ProxmoxAPI(backend_name="https", backend_type="async")
    async with ext_api as api:
        print(await api.version.get(filter_keys="version"))
        print(await api.cluster.ha.groups.get())
        nodes: list[dict] = await api.nodes.get(filter_keys=["node", "status"])
        if nodes:
            nodes = sorted([n.get("node") for n in nodes if n.get("status") == "online"])
        tasks = []
        # reuse previously opened client session by backend
        backend = api.backend
        print(type(backend))
        for node in nodes:
            new_api = ProxmoxAPI(backend=backend)
            tasks.append(
                new_api.nodes(node).status.get(
                    filter_keys=["kversion", "cpuinfo", "memory.total", "uptime"]
                )
            )
        print("Waiting for results... of resources: %s", len(tasks))
        results = await asyncio.gather(*tasks)
        for node, data in zip(nodes, results):
            if data is not None:
                data = {
                    "kversion": data.get("kversion", {}),
                    "cpus": data.get("cpuinfo", {}).get("cpus", {}),
                    "cpus_model": data.get("cpuinfo", {}).get("model", {}),
                    "memory_total": data.get("memory.total"),
                    "uptime":data.get("uptime", 0),
                }
            else:
                data = None
            print(data)
       

asyncio.run(async_main())
```

## Config file `config.toml`
```toml
DEBUG = false
NODES = []

[API]
TOKEN_ID = ""
TOKEN_SECRET = ""
BASE_URL = ""
ENTRY_POINT = "/api2/json"
VERIFY_SSL = true

[CLI]
ENTRY_POINT = "pvesh"

[SSH]
HOSTNAME = ""
USERNAME = ""
PASSWORD = ""
PORT = 22
AGENT = false
KEY_FILENAME = ""
```

## Redefine config values by .env file:
```dotenv
API_TOKEN_ID=user@pam!user_api
API_TOKEN_SECRET=XXXX-YYYY-.....
API_BASE_URL="https://proxmox.local:8006"

SSH_HOSTNAME="proxmox.local"
SSH_USERNAME="root"
```


## Debug
### Debug API
<details>
<summary>src/cluster_tasks/main.py</summary>

```commandline
DEBUG: Creating backend: https of type: sync
DEBUG: Formatted endpoint: /api2/json/version
INFO: 8.3.2
DEBUG: Formatted endpoint: /api2/json/cluster/ha/groups
INFO: [{'group': 'gr-04-05-06f', 'nodes': 'c04:30,c06:50,c05:40'}, {'group': 'gr-04-05f-06', 'nodes': 'c06:30,c05:50,c04:40'}, {'group': 'gr-02-03f-04', 'nodes': 'c04:30,c02:40,c03:50'}, {'group': 'gr-03-04f-05', 'nodes': 'c03:40,c04:50,c05:30'}, {'group': 'gr-05-06-07f', 'nodes': 'c07:50,c05:30,c06:40'}, {'group': 'test-group', 'nodes': 'c03,c02,c01:100'}, {'group': 'gr-03f-04-05', 'nodes': 'c03:50,c04:40,c05:30'}, {'group': 'gr-02f-03-04', 'nodes': 'c03:40,c04:30,c02:50'}, {'group': 'gr-01-02f-03', 'nodes': 'c03:30,c02:50,c01:40'}, {'group': 'gr-05-06f-07', 'nodes': 'c06:50,c05:40,c07:30'}, {'group': 'gr-06-07f-08', 'nodes': 'c06:40,c07:50,c08:30'}, {'group': 'gr-03-04-05f', 'nodes': 'c04:40,c05:50,c03:30'}, {'group': 'test-gr-02-03f-04', 'nodes': 'c04,c03,c02'}, {'group': 'gr-02-03-04f', 'nodes': 'c02:30,c04:50,c03:40'}, {'group': 'gr-01f-02-03', 'nodes': 'c02:40,c03:30,c01:50'}, {'group': 'gr-05f-06-07', 'nodes': 'c05:50,c07:30,c06:40'}, {'group': 'gr-04f-05-06', 'nodes': 'c04:50,c05:40,c06:30'}, {'group': 'gr-06f-07-08', 'nodes': 'c06:50,c07:40,c08:30'}, {'group': 'gr-01-02-03f', 'nodes': 'c01:30,c02:40,c03:50'}, {'group': 'gr-06-07-08f', 'nodes': 'c07:40,c06:30,c08:50'}]
DEBUG: Formatted endpoint: /api2/json/nodes/c01/status
INFO: 6.8.12-5-pve
DEBUG: Creating backend: https of type: async
DEBUG: Formatted endpoint: /api2/json/version
INFO: 8.3.2
DEBUG: Formatted endpoint: /api2/json/cluster/ha/groups
INFO: [{'group': 'gr-04-05-06f', 'nodes': 'c06:50,c05:40,c04:30'}, {'group': 'gr-04-05f-06', 'nodes': 'c06:30,c04:40,c05:50'}, {'group': 'gr-02-03f-04', 'nodes': 'c04:30,c02:40,c03:50'}, {'group': 'gr-03f-04-05', 'nodes': 'c05:30,c04:40,c03:50'}, {'group': 'gr-03-04f-05', 'nodes': 'c05:30,c03:40,c04:50'}, {'group': 'gr-05-06-07f', 'nodes': 'c06:40,c05:30,c07:50'}, {'group': 'test-group', 'nodes': 'c03,c01:100,c02'}, {'group': 'gr-06-07f-08', 'nodes': 'c08:30,c07:50,c06:40'}, {'group': 'gr-01-02f-03', 'nodes': 'c03:30,c02:50,c01:40'}, {'group': 'gr-05-06f-07', 'nodes': 'c07:30,c05:40,c06:50'}, {'group': 'gr-02f-03-04', 'nodes': 'c03:40,c04:30,c02:50'}, {'group': 'gr-05f-06-07', 'nodes': 'c05:50,c07:30,c06:40'}, {'group': 'gr-06-07-08f', 'nodes': 'c07:40,c06:30,c08:50'}, {'group': 'gr-01-02-03f', 'nodes': 'c02:40,c01:30,c03:50'}, {'group': 'gr-06f-07-08', 'nodes': 'c06:50,c08:30,c07:40'}, {'group': 'gr-04f-05-06', 'nodes': 'c05:40,c04:50,c06:30'}, {'group': 'gr-03-04-05f', 'nodes': 'c04:40,c05:50,c03:30'}, {'group': 'gr-02-03-04f', 'nodes': 'c03:40,c04:50,c02:30'}, {'group': 'gr-01f-02-03', 'nodes': 'c02:40,c03:30,c01:50'}, {'group': 'test-gr-02-03f-04', 'nodes': 'c02,c03,c04'}]
DEBUG: Formatted endpoint: /api2/json/nodes/c01/status
INFO: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'uptime': 551736}
DEBUG: Formatted endpoint: /api2/json/nodes/c01/status
INFO: 6.8.12-5-pve
```
</details>


<details>
<summary>src/cluster_tasks/debug_api.py</summary>

```commandline
INFO: ['c01', 'c02', 'c03', 'c04', 'c05', 'c06', 'c07', 'c08']
DEBUG: Creating backend: https of type: async
DEBUG: Formatted endpoint: /api2/json/version
INFO: 8.3.2
INFO: 

Debug_get_ha_groups

INFO: Waiting for results... of aget_ha_groups
DEBUG: Formatted endpoint: /api2/json/cluster/ha/groups
INFO: Total groups in cluster: 18
INFO: 1: Group: gr-02f-03-04 Nods: c02:50,c04:30,c03:40
INFO: 2: Group: gr-01-02f-03 Nods: c01:40,c02:50,c03:30
INFO: 3: Group: gr-05-06f-07 Nods: c06:50,c05:40,c07:30
INFO: 4: Group: gr-06-07f-08 Nods: c06:40,c08:30,c07:50
INFO: 5: Group: gr-03-04-05f Nods: c04:40,c05:50,c03:30
INFO: 6: Group: gr-01f-02-03 Nods: c01:50,c02:40,c03:30
INFO: 7: Group: gr-02-03-04f Nods: c02:30,c04:50,c03:40
INFO: 8: Group: gr-05f-06-07 Nods: c05:50,c06:40,c07:30
INFO: 9: Group: gr-06-07-08f Nods: c08:50,c06:30,c07:40
INFO: 10: Group: gr-06f-07-08 Nods: c08:30,c07:40,c06:50
INFO: 11: Group: gr-01-02-03f Nods: c01:30,c02:40,c03:50
INFO: 12: Group: gr-04f-05-06 Nods: c05:40,c04:50,c06:30
INFO: 13: Group: gr-04-05-06f Nods: c04:30,c06:50,c05:40
INFO: 14: Group: gr-04-05f-06 Nods: c05:50,c04:40,c06:30
INFO: 15: Group: gr-02-03f-04 Nods: c03:50,c02:40,c04:30
INFO: 16: Group: gr-05-06-07f Nods: c06:40,c07:50,c05:30
INFO: 17: Group: gr-03-04f-05 Nods: c05:30,c04:50,c03:40
INFO: 18: Group: gr-03f-04-05 Nods: c04:40,c03:50,c05:30
INFO: 

Debug_create_ha_group

INFO: List live nodes:
DEBUG: Formatted endpoint: /api2/json/nodes
INFO: ['c01', 'c02', 'c04', 'c05', 'c06', 'c07', 'c08']
INFO: List groups:
DEBUG: Formatted endpoint: /api2/json/cluster/ha/groups
INFO: ['gr-03f-04-05', 'gr-05-06-07f', 'gr-03-04f-05', 'gr-04-05f-06', 'gr-04-05-06f', 'gr-02-03f-04', 'gr-05f-06-07', 'gr-04f-05-06', 'gr-06f-07-08', 'gr-06-07-08f', 'gr-01-02-03f', 'gr-03-04-05f', 'gr-01f-02-03', 'gr-02-03-04f', 'gr-06-07f-08', 'gr-02f-03-04', 'gr-01-02f-03', 'gr-05-06f-07']
INFO: Create group: test-gr-02-03f-04, for nodes: c01,c02,c04
DEBUG: Formatted endpoint: /api2/json/cluster/ha/groups
INFO: None
INFO: Get created group: test-gr-02-03f-04
DEBUG: Formatted endpoint: /api2/json/cluster/ha/groups/test-gr-02-03f-04
INFO: {'group': 'test-gr-02-03f-04', 'nodes': 'c01,c04,c02'}
INFO: Delete group: test-gr-02-03f-04
DEBUG: Formatted endpoint: /api2/json/cluster/ha/groups/test-gr-02-03f-04
INFO: None
INFO: List groups:
DEBUG: Formatted endpoint: /api2/json/cluster/ha/groups
INFO: ['gr-04-05f-06', 'gr-04-05-06f', 'gr-02-03f-04', 'gr-03-04f-05', 'gr-05-06-07f', 'gr-03f-04-05', 'gr-02f-03-04', 'gr-01-02f-03', 'gr-05-06f-07', 'gr-06-07f-08', 'gr-03-04-05f', 'gr-02-03-04f', 'gr-01f-02-03', 'gr-05f-06-07', 'gr-04f-05-06', 'gr-06f-07-08', 'gr-06-07-08f', 'gr-01-02-03f']
INFO: 

Debug_get_node_status_sequenced

DEBUG: Formatted endpoint: /api2/json/nodes
INFO: ['c01', 'c02', 'c04', 'c05', 'c06', 'c07', 'c08']
INFO: c01
DEBUG: Formatted endpoint: /api2/json/nodes/c01/status
INFO: c02
DEBUG: Formatted endpoint: /api2/json/nodes/c02/status
INFO: c04
DEBUG: Formatted endpoint: /api2/json/nodes/c04/status
INFO: c05
DEBUG: Formatted endpoint: /api2/json/nodes/c05/status
INFO: c06
DEBUG: Formatted endpoint: /api2/json/nodes/c06/status
INFO: c07
DEBUG: Formatted endpoint: /api2/json/nodes/c07/status
INFO: c08
DEBUG: Formatted endpoint: /api2/json/nodes/c08/status
INFO: Waiting for results... of resources: 0
INFO: Node: c01, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '6 days, 11:34:17'}
INFO: Node: c02, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '6 days, 11:33:59'}
INFO: Node: c04, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '6 days, 11:34:12'}
INFO: Node: c05, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '6 days, 11:34:08'}
INFO: Node: c06, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '4 days, 0:32:50'}
INFO: Node: c07, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '125.85 GB', 'uptime': '6 days, 11:34:05'}
INFO: Node: c08, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '125.85 GB', 'uptime': '6 days, 11:34:01'}
INFO: 

Debug_get_node_status_parallel

DEBUG: Formatted endpoint: /api2/json/nodes
INFO: ['c01', 'c02', 'c04', 'c05', 'c06', 'c07', 'c08']
DEBUG: <class 'ext_api.backends.backend_https.ProxmoxAsyncHTTPSBackend'>
INFO: c01
INFO: c02
INFO: c04
INFO: c05
INFO: c06
INFO: c07
INFO: c08
INFO: Waiting for results... of resources: 7
DEBUG: Formatted endpoint: /api2/json/nodes/c01/status
DEBUG: Formatted endpoint: /api2/json/nodes/c02/status
DEBUG: Formatted endpoint: /api2/json/nodes/c04/status
DEBUG: Formatted endpoint: /api2/json/nodes/c05/status
DEBUG: Formatted endpoint: /api2/json/nodes/c06/status
DEBUG: Formatted endpoint: /api2/json/nodes/c07/status
DEBUG: Formatted endpoint: /api2/json/nodes/c08/status
INFO: Node: c01, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '6 days, 11:34:19'}
INFO: Node: c02, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '6 days, 11:34:01'}
INFO: Node: c04, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '6 days, 11:34:14'}
INFO: Node: c05, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '6 days, 11:34:09'}
INFO: Node: c06, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '4 days, 0:32:51'}
INFO: Node: c07, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '125.85 GB', 'uptime': '6 days, 11:34:06'}
INFO: Node: c08, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '125.85 GB', 'uptime': '6 days, 11:34:01'}
```
</details>
