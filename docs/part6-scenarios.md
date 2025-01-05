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
      vmid: 1004
      newid: 201
      name: "Cloned01"
      full: 1
```

#### Result
<details>
<summary>src/cluster_tasks/controller_sync.py</summary>

``` pycon
python /src/cluster_tasks/controller_sync.py 
DEBUG: Scenarios config: <config.config.ConfigLoader object at 0x10fd0b350>
DEBUG: Creating backend: https of type: sync
Running Scenario Template VM Clone: ScenarioCloneTemplateVmSync
DEBUG: Generated a new task ID: 036b0cf8-c506-42ae-bb16-41f79d8708d2
DEBUG: Formatted endpoint: /api2/json/nodes/c01/qemu/201/status/current
INFO: VM 201 already exists - Deleting...
DEBUG: Generated a new task ID: d851e29d-11b9-49f0-ac48-b4be53f66a47
DEBUG: Formatted endpoint: /api2/json/nodes/c01/qemu/201
DEBUG: Generated a new task ID: fb7e60d4-9f45-490b-ba48-c2b7c408f297
DEBUG: Formatted endpoint: /api2/json/nodes/c01/tasks/UPID:c01:002DC36D:045F99E0:677A9183:qmdestroy:201:api_user@pam!cluster_helper:/status
INFO: Waiting for task to finish... [ 0:00:00 / 0:01:00 ]
DEBUG: Generated a new task ID: cb281c02-d5de-4f5e-9362-11f83e261250
DEBUG: Formatted endpoint: /api2/json/nodes/c01/tasks/UPID:c01:002DC36D:045F99E0:677A9183:qmdestroy:201:api_user@pam!cluster_helper:/status
INFO: VM 201 deleted successfully
DEBUG: Generated a new task ID: 1f3ce5b8-2ac1-4889-b43c-5ddfc76b949a
DEBUG: Formatted endpoint: /api2/json/nodes/c01/qemu/1004/clone
DEBUG: Generated a new task ID: 2bb19080-44ab-43ce-9b30-a3d8c4d0c51f
DEBUG: Formatted endpoint: /api2/json/nodes/c01/tasks/UPID:c01:002DC388:045F9AE2:677A9185:qmclone:1004:api_user@pam!cluster_helper:/status
INFO: Waiting for task to finish... [ 0:00:00 / 0:01:00 ]
DEBUG: Generated a new task ID: 3398e65b-ddad-427b-af86-ee2735e54907
DEBUG: Formatted endpoint: /api2/json/nodes/c01/tasks/UPID:c01:002DC388:045F9AE2:677A9185:qmclone:1004:api_user@pam!cluster_helper:/status
INFO: Waiting for task to finish... [ 0:00:02 / 0:01:00 ]
DEBUG: Generated a new task ID: 6cafba81-fa97-48a8-9b51-c11df3bbe1d8
DEBUG: Formatted endpoint: /api2/json/nodes/c01/tasks/UPID:c01:002DC388:045F9AE2:677A9185:qmclone:1004:api_user@pam!cluster_helper:/status
INFO: Waiting for task to finish... [ 0:00:04 / 0:01:00 ]
DEBUG: Generated a new task ID: 507cb3aa-7a72-4b01-b1f0-9a52a8f92b99
DEBUG: Formatted endpoint: /api2/json/nodes/c01/tasks/UPID:c01:002DC388:045F9AE2:677A9185:qmclone:1004:api_user@pam!cluster_helper:/status
INFO: Waiting for task to finish... [ 0:00:06 / 0:01:00 ]
DEBUG: Generated a new task ID: f4cb2983-3d06-49d0-b221-6336da330ce1
DEBUG: Formatted endpoint: /api2/json/nodes/c01/tasks/UPID:c01:002DC388:045F9AE2:677A9185:qmclone:1004:api_user@pam!cluster_helper:/status
INFO: VM 201 cloned successfully

Process finished with exit code 0
```
</details>

### ScenarioFactory

```python
scenario = ScenarioFactory.create_scenario(scenario_file, config)
```


### ScenarioBase





[README](../README.md)