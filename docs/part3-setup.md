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


### Run
Need to define env variables for `PYTHONPATH` to src folder before running main.py
```commandline
python main.py --h         
usage: Proxmox Cluster Tasks [-h] [--debug {true,false,none}] [--sync] [--concurrent]

options:
  -h, --help            show this help message and exit
  --debug {true,false,none}
                        Enable or disable debug mode (true, false, none)
  --sync                Run in sync mode, default is async mode
  --concurrent          Run scenarios concurrently; defaults to running sequentially.
```

### Concurrency Run Example

You can run scenarios concurrently using the `--concurrent` option. This utilizes a thread pool to execute tasks in parallel, improving execution time for multiple scenarios.

#### Command

```bash
python main.py --concurrent
```

#### Output
<details>
<summary>python main.py  --concurrent </summary>

```commandline
python main.py  --concurrent  
INFO: Running Scenario Template VM Clone: ScenarioCloneTemplateVmAsync
INFO: Checking if VM 202 already exists
INFO: Running Scenario Template VM Clone: ScenarioCloneTemplateVmAsync
INFO: Checking if VM 203 already exists
INFO: VM 202 already exists on node:'c02'. Deleting...
INFO: VM 203 already exists on node:'c03'. Deleting...
INFO: Waiting for task to finish... [ 0:00:00 / 0:10:00 ]
INFO: VM 203 deleted successfully
INFO: Cloning VM from 1004 to 203
INFO: Waiting for task to finish... [ 0:00:00 / 0:10:00 ]
INFO: VM 202 deleted successfully
INFO: Cloning VM from 1004 to 202
INFO: Waiting for task to finish... [ 0:00:00 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:02 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:02 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:04 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:04 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:06 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:06 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:08 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:08 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:11 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:11 / 0:10:00 ]
INFO: VM 203 cloned successfully
INFO: Configuring Network for VM 203
INFO: Configured Network for VM 203 successfully
INFO: Configuring tags for VM 203
INFO: VM 203 configured tags:'tag1,dot-003,ip-192-0-2-3' successfully
INFO: Migrating VM 203 to node: c03
INFO: Waiting for task to finish... [ 0:00:00 / 0:10:00 ]
INFO: VM 202 cloned successfully
INFO: Configuring Network for VM 202
INFO: Configured Network for VM 202 successfully
INFO: Configuring tags for VM 202
INFO: VM 202 configured tags:'tag1,dot-002,ip-192-0-2-2' successfully
INFO: Migrating VM 202 to node: c02
INFO: Waiting for task to finish... [ 0:00:00 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:02 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:02 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:04 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:04 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:06 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:06 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:08 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:08 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:11 / 0:10:00 ]
INFO: Waiting for task to finish... [ 0:00:11 / 0:10:00 ]
INFO: VM 203 migrated successfully
INFO: Scenario ScenarioCloneTemplateVmAsync completed successfully
INFO: VM 202 migrated successfully
INFO: Scenario ScenarioCloneTemplateVmAsync completed successfully
INFO: MAIN: Finished
```
</details>

#### Notes
    The exact output may vary depending on the logging configuration and the scenarios being executed.


[README](../README.md)
