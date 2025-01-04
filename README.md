# Proxmox Cluster Tasks

## Purpose of the Project

The **Proxmox Cluster Tasks** repository is designed to simplify and automate daily administrative tasks within a Proxmox Virtual Environment (VE) cluster. The project focuses on enhancing the efficiency of cluster management by providing tools and wrappers for interacting with Proxmox through various backends and APIs.

### Key Features

#### Daily Task Automation
- **Clone VMs from Templates**: Easily create virtual machines based on predefined templates.
- **Distribute Cloned VMs Across Nodes**: Automatically balance VM distribution across cluster nodes.
- **Configure VM Settings**:
  - **Replication**: Set up replication policies for high availability.
  - **Backup**: Automate backup configurations.
  - **Networking**: Configure network interfaces and firewall rules.
- **High Availability (HA) Settings**:
  - Define HA groups and priorities for VMs.
  - For example, deploy `instance_02` on node `c02`, configure replication to nodes `c01` and `c03`, and assign HA settings prioritizing `c02`.

#### Multi-Backend Support
- **HTTPS**: Direct API interaction using an HTTPS wrapper.
- **CLI**: Programmatic execution of Proxmox CLI commands.
- **SSH**: Manage clusters securely over SSH.

#### Flexible Execution Modes
- **Asynchronous Mode**: Perform non-blocking, concurrent operations for time-sensitive tasks.
- **Synchronous Mode**: Sequential execution for straightforward tasks.

---

The primary goal of this project is to streamline Proxmox VE cluster management, reduce manual effort, and improve operational consistency.


## API Reference
- [Proxmox VE API Documentation](https://pve.proxmox.com/wiki/Proxmox_VE_API)
- [Proxmox VE API Viewer](https://pve.proxmox.com/pve-docs/api-viewer)

---

## Setup

### Backends
Supported backends:
```python
BACKENDS_NAMES = ["https", "cli", "ssh"]
```

#### Automatically Register Backends
To use backends, you can register all available backends or a specific subset using a configuration file with `register_backends()`:

```python
# Register all backends
register_backends()

# Register a single backend
register_backends("https")

# Register specific backends
register_backends(["https", "ssh"])
```

Backends are available for both synchronous and asynchronous code.

#### Manually Create an Instance of a Backend
Alternatively, you can manually create a backend instance by importing the corresponding module:

```python
from ext_api.backends.backend_https import ProxmoxHTTPSBackend

backend = ProxmoxHTTPSBackend(
    base_url="<BASE_URL>",
    entry_point="<ENTRY_POINT>",
    token="<TOKEN>",
    verify_ssl=True
)
```

---

### ProxmoxAPI Class
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

#### Example: Multiple Parallel requests with same API Instance (https in Async Mode)
In this example, one API instances with reusing the same backend session are created and used in parallel for asynchronous operations:
```python
async def async_main():
    register_backends("https")
    ext_api = ProxmoxAPI(backend_name="https", backend_type="async")
    async with ext_api as api:
        tasks = []
        for _ in range(8):
            logger.info(len(tasks))
            tasks.append(api.api.version.get(filter_keys="version"))
        logger.info("Waiting for results... of resources: %s", len(tasks))
        results = await asyncio.gather(*tasks)
        logger.info(results)
```
Results:
```log
DEBUG: Creating backend: https of type: async
INFO: 0
DEBUG: NEW task_id: 4be8ee71-218d-43ff-b62a-6fb15827bfe0
INFO: 1
DEBUG: NEW task_id: a55c5863-5634-4a2f-a379-9eb73046caa0
INFO: 2
DEBUG: NEW task_id: 8399e980-a6d6-4225-902f-3bcd7a504b7c
INFO: 3
DEBUG: NEW task_id: eea05041-1415-43ab-8c79-c1f48daed260
INFO: 4
DEBUG: NEW task_id: 42add8a3-e2c4-4206-ac83-ba694c3b9ed2
INFO: 5
DEBUG: NEW task_id: 4fd30c33-67c2-42f0-8150-67e27ca5ac45
INFO: 6
DEBUG: NEW task_id: 58e011e8-9eec-412b-b483-298487a002d8
INFO: 7
DEBUG: NEW task_id: 6957e51c-d8e4-4787-9adf-d5960a46f2b0
INFO: Waiting for results... of resources: 8
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: Formatted endpoint: /api2/json/version
INFO: ['8.3.2', '8.3.2', '8.3.2', '8.3.2', '8.3.2', '8.3.2', '8.3.2', '8.3.2']
```

#### Example: Multiple Parallel with  many API Instances (https in Async Mode)
In this example, multiple API instances with reusing the same backend session are created and used in parallel for asynchronous operations:
```python
async def async_main():
    register_backends("https")
    ext_api = ProxmoxAPI(backend_name="https", backend_type="async")
    async with ext_api as api:
        print(await api.version.get(filter_keys="version"))
        print(await api.cluster.ha.groups.get())
        nodes = await api.nodes.get(filter_keys=["node", "status"])
        if nodes:
            nodes = sorted([n.get("node") for n in nodes if n.get("status") == "online"])
        tasks = []
        backend = api.backend
        for node in nodes:
            new_api = ProxmoxAPI(backend=backend)
            tasks.append(new_api.nodes(node).status.get(filter_keys=["kversion", "cpuinfo", "memory.total", "uptime"]))
        results = await asyncio.gather(*tasks)
        for node, data in zip(nodes, results):
            print(data)

asyncio.run(async_main())
```
This example demonstrates the ability to handle multiple API instances, enabling efficient parallel operations while reusing the same backend session. This approach is ideal for scenarios where data from multiple nodes needs to be fetched concurrently.

#### Example of Low-Level Requests (Async)

For more advanced use cases, you can perform low-level API requests directly:

##### Solution 1: Prepare and Execute the Request Manually

```python
# Extract the request parameters for the desired endpoint
params = api.version.get(get_request_param=True)

# Perform the asynchronous request using the extracted parameters
response = await api.async_request(**params)

# Analyze the response to filter and extract specific data
print(api._response_analyze(response, filter_keys="version"))
```

##### Solution 2: Simplified Execution with Built-in API Method
```python
# Use the internal execution method directly with request parameters
print(await api._async_execute(params=params, filter_keys="version"))
```

#### Example of Low-Level Parallel Requests Using the Same API Instance (Async)

Perform parallel requests for multiple nodes while reusing the same API instance:

```python
# Prepare tasks for parallel execution
tasks = []
for node in nodes:
    print(node)  # Log or display the current node
    params = api.nodes(node).status.get(get_request_param=True)
    
    # Add the task to the list using the internal execution method
    tasks.append(
        api._async_execute(
            params=params,
            filter_keys=["kversion", "cpuinfo", "memory.total", "uptime"],
        )
    )

# Wait for all tasks to complete and collect results
print("Waiting for results... Number of resources:", len(tasks))
results = await asyncio.gather(*tasks)    
```

#### Example of Parallel Requests Using the Queue of pre created API Instances in Thread Pool (Sync)

```python
import queue
from concurrent.futures import ThreadPoolExecutor

from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI
MAX_THREADS = 4

register_backends("https")
clients = [ProxmoxAPI(backend_name="https") for _ in range(MAX_THREADS)]
client_queue = queue.Queue()

# Populate the queue with clients
for c in clients:
    client_queue.put(c)

def get_version():
    client = client_queue.get()
    try:
        # Get an available client from the queue
        with client as api:
            response = api.version.get()
        return response
    finally:
        # Return the client to the queue
        client_queue.put(client)
        
tasks = []
with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    for _ in range(8):
        print(f"Task submit: {len(tasks)}")
        tasks.append(executor.submit(get_version))
print("futures created")
results = [task.result() for task in tasks]
print(results)
```
Results:
```log
DEBUG: Creating backend: https of type: sync
DEBUG: Creating backend: https of type: sync
DEBUG: Creating backend: https of type: sync
DEBUG: Creating backend: https of type: sync
DEBUG: Task submit: 0
DEBUG: Task submit: 1
DEBUG: Task submit: 2
DEBUG: Task submit: 3
DEBUG: Task submit: 4
DEBUG: Task submit: 5
DEBUG: Task submit: 6
DEBUG: Task submit: 7
DEBUG: NEW task_id: 6f8c5d7b-52ac-42db-bf1e-3e3314ac36a9
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: NEW task_id: eb986b66-77ef-41f5-9282-e627fea07407
DEBUG: NEW task_id: 61950227-42ff-4923-b16c-a565d8430394
DEBUG: NEW task_id: 45359f3c-9821-4ff4-99c1-1338b396cd48
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: NEW task_id: 838ab521-5687-4ae1-8c73-6bd7f9567b66
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: NEW task_id: 2332882c-1ab9-48da-98bf-c54295c37761
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: NEW task_id: 6d4770b3-0a04-4f4f-8b10-373112b1fae9
DEBUG: Formatted endpoint: /api2/json/version
DEBUG: NEW task_id: d79ebba9-581e-46a0-a076-b607ae4012e4
DEBUG: Formatted endpoint: /api2/json/version
futures created
['8.3.2', '8.3.2', '8.3.2', '8.3.2', '8.3.2', '8.3.2', '8.3.2', '8.3.2']
```

These examples provide flexibility for advanced API usage, allowing you to control request preparation and execution explicitly, even in parallel scenarios.

## Filtering Results

The API supports filtering the response to return only the desired keys. The behavior of the `filter_keys` parameter depends on the structure of the result.

### Behavior of `filter_keys`

1. **If the result is a dictionary (`dict`):**
   - `filter_keys="key"`: Returns the plain string value associated with the key.
   - `filter_keys=["key1", "key2"]`: Returns a new dictionary containing only the specified keys and their values.

2. **If the result is a list of dictionaries (`list[dict]`):**
   - `filter_keys=["key1", "key2"]`: Filters each dictionary in the list to include only the specified keys.

3. **For nested dictionaries:**
   - Use dot notation in `filter_keys` to specify keys within nested dictionaries.  
     For example, `filter_keys=["parent.child", "parent.another_child"]` will retrieve the nested values within the parent dictionary.

### Examples

#### Filtering a Dictionary
```python
response = {
    "version": "7.4",
    "release_date": "2023-10-01",
    "features": ["feature1", "feature2"]
}

# Example 1: Single key
print(api._response_analyze(response, filter_keys="version"))
# Output: "7.4"

# Example 2: Multiple keys
print(api._response_analyze(response, filter_keys=["version", "release_date"]))
# Output: {"version": "7.4", "release_date": "2023-10-01"}
```
#### Filtering a List of Dictionaries
```python
response = [
    {"node": "node1", "status": "online", "cpu": "8 cores"},
    {"node": "node2", "status": "offline", "cpu": "4 cores"},
]

# Filter specific keys
print(api._response_analyze(response, filter_keys=["node", "status"]))
# Output: [{"node": "node1", "status": "online"}, {"node": "node2", "status": "offline"}]
```
#### Filtering Nested Dictionaries
```python
response = {
    "cluster": {
        "name": "cluster1",
        "status": {"online_nodes": 3, "offline_nodes": 1},
    }
}

# Filter nested keys using dot notation
print(api._response_analyze(response, filter_keys=["cluster.name", "cluster.status.online_nodes"]))
# Output: {"cluster.name": "cluster1", "cluster.status.online_nodes": 3}
```
By specifying the desired keys with filter_keys, you can efficiently retrieve only the data you need.

This section clearly outlines how filtering works with examples for different data structures, including nested dictionaries.



## Configuration

### `config.toml` File
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

### Overriding Configuration with `.env` File
```dotenv
API_TOKEN_ID=user@pam!user_api
API_TOKEN_SECRET=XXXX-YYYY-.....
API_BASE_URL=https://proxmox.local:8006

SSH_HOSTNAME=proxmox.local
SSH_USERNAME=root
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

## Acknowledgments

Special thanks to the [proxmoxer](https://github.com/proxmoxer/proxmoxer) project for providing inspiration and solutions that influenced the development of this library.

