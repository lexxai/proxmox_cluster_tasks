### ProxmoxAPI Class. Examples. Advanced Concurrent Usage and Low-Level API Requests


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
            tasks.append(api.version.get(filter_keys="version"))
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
