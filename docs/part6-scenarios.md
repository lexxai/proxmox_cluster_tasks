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
│   ├── clone_template_vm_async.py (class ScenarioCloneTemplateVmAsync)
│   ├── clone_template_vm_sync.py  (class ScenarioCloneTemplateVmSync)
````
#### Scenarios config `scenarios_configs.yaml`
```yaml
API:
  backend: "https"
Scenarios:
  CloneTemplateVM:
    file: "clone_template_vm"
    config:
      node: "c01"
      destination_node: "c02"
      source_vm_id: 1004
      destination_vm_id: 201
      overwrite_destination: True
      name: "Cloned01"
      network:
        ip: "192.0.2.1/24"
        increase_ip: 1
      full: 1
```
#### VM network
The cloned VM can either retain the network settings of the source VM or be assigned a new network configuration. 
This flexibility allows for maintaining existing values or updating them as needed.

* ip (str): The final IP address with its mask for the new VM, derived from the configuration or the source VM.
* gw (str): The final gateway IP address for the new VM, derived from the configuration or the source VM.
* increase_ip (int): The value to increment the IP address by.
* decrease_ip (int): The value to decrement the IP address by.
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

``` pycon
python /src/cluster_tasks/main.py
INFO: Running Scenario Template VM Clone: ScenarioCloneTemplateVmAsync
INFO: Checking if VM 201 already exists
INFO: VM 201 already exists on node:'c02'. Deleting...
INFO: Waiting for task to finish... [ 0:00:00 / 0:01:00 ]
INFO: VM 201 deleted successfully
INFO: Cloning VM from 1004 to 201
INFO: Waiting for task to finish... [ 0:00:00 / 0:01:00 ]
INFO: Waiting for task to finish... [ 0:00:02 / 0:01:00 ]
INFO: Waiting for task to finish... [ 0:00:04 / 0:01:00 ]
INFO: Waiting for task to finish... [ 0:00:06 / 0:01:00 ]
INFO: VM 201 cloned successfully
INFO: Configuring Network for VM 201
INFO: Configured Network for VM 201 successfully
INFO: Migrating VM 201 to node: c02
INFO: Waiting for task to finish... [ 0:00:00 / 0:01:00 ]
INFO: Waiting for task to finish... [ 0:00:02 / 0:01:00 ]
INFO: Waiting for task to finish... [ 0:00:04 / 0:01:00 ]
INFO: Waiting for task to finish... [ 0:00:06 / 0:01:00 ]
INFO: Waiting for task to finish... [ 0:00:08 / 0:01:00 ]
INFO: Waiting for task to finish... [ 0:00:11 / 0:01:00 ]
INFO: VM 201 migrated successfully
INFO: Scenario ScenarioCloneTemplateVmAsync completed successfully

Process finished with exit code 0
```
</details>

### ScenarioFactory

```python
scenario = ScenarioFactory.create_scenario(scenario_file, config)
```


### ScenarioBase





[README](../README.md)