## Scenarios

### Setup 

Example:
```python
    config_file = Path(__file__).parent / "scenarios_configs.yaml"
    scenarios_config = ConfigLoader(file_path=config_file)
    backend_name = scenarios_config.get("API.backend", "https")
    register_backends(backend_name)
    ext_api = ProxmoxAPI(backend_name=backend_name, backend_type="sync")
    with ext_api as api:
        node_tasks = NodeTasksSync(api=api)  # Pass the api instance to NodeTasksAsync
        for v in scenarios_config.get("Scenarios").values():
            scenario_file = v.get("file")
            config = v.get("config")
            # Create scenario instance using the factory
            scenario = ScenarioFactory.create_scenario(scenario_file, config)
            # Run the scenario
            scenario.run(node_tasks)
```

### Config
#### Folder tree

```bash
cluster_tasks
├── scenarios_configs.yaml
├── scenarios
│   ├── clone_template_vm_base.py  (class ScenarioCloneTemplateVmBase)
│   ├── clone_template_vm_async.py (class ScenarioCloneTemplateVmAsync)
│   ├── clone_template_vm_sync.py  (class ScenarioCloneTemplateVmSync)
````
#### Scenarios config `scenarios_configs.yaml`
```yaml
API:
  backend: "https"
Scenarios:
  CloneTemplateVM-2:
    file: "clone_template_vm"
    config:
      node: "c01"
      destination_node: "c02"
      source_vm_id: 1004
      destination_vm_id: 202
      overwrite_destination: True
      name: "Cloned01"
      network:
        ip: "192.0.2.0/24"
        increase_ip: 2
      tags: ["tag1", "dot-{vm_dot_ip}","ip-{vm_ip}"]
      full: True
  CloneTemplateVM-3:
    file: "clone_template_vm"
    config:
      node: "c01"
      destination_node: "c03"
      source_vm_id: 1004
      destination_vm_id: 203
      overwrite_destination: True
      name: "Cloned03"
      network:
        ip: "192.0.2.0/24"
        increase_ip: 3
      tags: ["tag1", "dot-{vm_dot_ip}","ip-{vm_ip}"]
      full: True
```
#### VM network
The cloned VM can either retain the network settings of the source VM or be assigned a new network configuration. 
This flexibility allows for maintaining existing values or updating them as needed.

* ip (str): The final IP address with its mask for the new VM, derived from the configuration or the source VM.
* gw (str): The final gateway IP address for the new VM, derived from the configuration or the source VM.
* increase_ip (int): The value to increment the final IP address by.
* decrease_ip (int): The value to decrement the final IP address by.
```yaml
      network:
        ip: "{ip}/{subnet}"
        gw: "{gw}"
        increase_ip: {number}
        decrease_ip: {number}
```

#### Result Running Scenario Template VM Clone
<details>
<summary>src/cluster_tasks/main.py</summary>

``` bash
INFO: *** Running Scenario Template VM Clone: 'CloneTemplateVM-2'
INFO: Checking if destination Node:'c02' is online
INFO: Checking if VM 202 already exists
INFO: VM 202 already exists on node:'c02'. Deleting...
INFO: Waiting for task (c02:0038BA3D:0557BA28:677D0CC9:qmdestroy:202) to finish... [ 0:00:00 / 0:10:00 ]
INFO: VM 202 deleted successfully
INFO: Cloning VM from 1004 to 202
INFO: Waiting for task (c01:00381E06:0557C232:677D0CCB:qmclone:1004) to finish... [ 0:00:00 / 0:10:00 ]
INFO: Waiting for task (c01:00381E06:0557C232:677D0CCB:qmclone:1004) to finish... [ 0:00:02 / 0:10:00 ]
INFO: Waiting for task (c01:00381E06:0557C232:677D0CCB:qmclone:1004) to finish... [ 0:00:04 / 0:10:00 ]
INFO: Waiting for task (c01:00381E06:0557C232:677D0CCB:qmclone:1004) to finish... [ 0:00:06 / 0:10:00 ]
INFO: Waiting for task (c01:00381E06:0557C232:677D0CCB:qmclone:1004) to finish... [ 0:00:08 / 0:10:00 ]
INFO: VM 202 cloned successfully
INFO: Configuring Network for VM 202
INFO: Configured Network for VM 202 successfully
INFO: Configuring tags for VM 202
INFO: VM 202 configured tags:'tag1,dot-002,ip-192-0-2-2' successfully
INFO: Migrating VM 202 to node: c02
INFO: Waiting for task (c01:00381E6F:0557C703:677D0CD8:qmigrate:202) to finish... [ 0:00:00 / 0:10:00 ]
INFO: Waiting for task (c01:00381E6F:0557C703:677D0CD8:qmigrate:202) to finish... [ 0:00:02 / 0:10:00 ]
INFO: Waiting for task (c01:00381E6F:0557C703:677D0CD8:qmigrate:202) to finish... [ 0:00:04 / 0:10:00 ]
INFO: Waiting for task (c01:00381E6F:0557C703:677D0CD8:qmigrate:202) to finish... [ 0:00:06 / 0:10:00 ]
INFO: Waiting for task (c01:00381E6F:0557C703:677D0CD8:qmigrate:202) to finish... [ 0:00:08 / 0:10:00 ]
INFO: Waiting for task (c01:00381E6F:0557C703:677D0CD8:qmigrate:202) to finish... [ 0:00:11 / 0:10:00 ]
INFO: VM 202 migrated successfully
INFO: *** Scenario 'CloneTemplateVM-2' completed successfully
INFO: *** Running Scenario Template VM Clone: 'CloneTemplateVM-3'
INFO: Checking if destination Node:'c03' is online
ERROR: Failed to run scenario 'CloneTemplateVM-3': Node:'c03' is offline
INFO: Proxmox Cluster Tasks: Finished
Process finished with exit code 0
```
</details>

### ScenarioFactory

```python
scenario = ScenarioFactory.create_scenario(scenario_file, config)
```


### ScenarioBase





[README](../README.md)