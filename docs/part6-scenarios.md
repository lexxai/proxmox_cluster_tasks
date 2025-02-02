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

The configuration files for the project are located in the `configs/` folder:

- **General Configuration**: Defined in `configs/configs.toml`.
- **Scenarios Configuration**: Defined in `configs/scenarios_configs.yaml`.

When running the package using `python -m proxmox-cluster-tasks` or `proxmox-cluster-tasks`, the application searches for the `configs/` folder in the current working directory where the command is executed.

If the folder is not found in the working directory, the application defaults to using the `configs/` folder located in the package root directory.

#### Custom Config Paths

The paths to the configuration files can be customized using the following parameters in the `main` function:

- `--config_file`: Specifies the path to the general configuration file.
- `--scenarios_config_file`: Specifies the path to the scenarios configuration file.

This flexibility allows users to override default configurations and tailor the application to their specific requirements.

#### Folder tree

```bash
cluster_tasks
├── scenarios
│   ├── clone_template_vm_base.py  (class ScenarioCloneTemplateVmBase)
│   ├── clone_template_vm_async.py (class ScenarioCloneTemplateVmAsync)
│   ├── clone_template_vm_sync.py  (class ScenarioCloneTemplateVmSync)
````
#### Scenarios config `configs/scenarios_configs.yaml`
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
      full: True
      name: "Cloned01"
      network:
        ip: "192.0.2.0/24"
        increase_ip: 2
      tags: ["tag1", "dot-{vm_dot_ip}","ip-{vm_ip}"]
      pool_id: "cxx"
      replications:
        - node: "c04"
          schedule: "*/30"
          rate: 50.0
          comment: "Replication to c04"
          disable: False
        - node: "c05"
        - node: "c07"
          schedule: "*/30"
      ha:
        group: "gr-02f-04-05-07"
        nodes: "c02:100,c04,c05,c07"
        overwrite: True
        resource:
          create: True
          overwrite: True
          state: "ignored"
          comment: "HA resource for VM 202"
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
<summary>src/main.py</summary>

``` bash
This action is dangerous. Are you sure you want to continue? (yes/no): yes
INFO: *** Running Scenario Template VM Clone: 'CloneTemplateVM-2'
INFO: Checking if destination Node:'c02' is online
INFO: Checking if VM 202 already exists
INFO: VM 202 already exists on node:'c02'. Deleting...
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:00 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:02 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:04 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:06 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:08 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:11 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:13 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:15 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:17 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:19 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:21 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:24 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:26 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:28 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:30 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:32 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:35 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:37 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:39 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:41 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:43 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:45 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:48 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:50 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:52 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:54 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:56 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:00:59 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:01:01 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:01:03 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:01:05 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:01:07 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:01:09 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:01:12 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:01:14 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:01:16 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:01:18 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:01:20 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:01:23 / 0:10:00 ]
INFO: Waiting for replication job (202 to any) is removed... [ 0:01:25 / 0:10:00 ]
INFO: VM 202 deleting resource ...
INFO: Waiting for task (c02:00102A17:0178A96E:6786EFBD:qmdestroy:202) to finish... [ 0:00:00 / 0:10:00 ]
INFO: VM 202 deleted successfully
INFO: Cloning VM from 1004 to 202
INFO: Waiting for task (c01:000FAED7:0178AC63:6786EFC0:qmclone:1004) to finish... [ 0:00:00 / 0:10:00 ]
INFO: Waiting for task (c01:000FAED7:0178AC63:6786EFC0:qmclone:1004) to finish... [ 0:00:02 / 0:10:00 ]
INFO: Waiting for task (c01:000FAED7:0178AC63:6786EFC0:qmclone:1004) to finish... [ 0:00:04 / 0:10:00 ]
INFO: Waiting for task (c01:000FAED7:0178AC63:6786EFC0:qmclone:1004) to finish... [ 0:00:06 / 0:10:00 ]
INFO: VM 202 cloned successfully
INFO: Configuring Network for VM 202
INFO: Configured Network for VM 202 successfully
INFO: Configuring tags for VM 202
INFO: VM 202 configured tags:'tag1,dot-002,ip-192-0-2-2' successfully
INFO: Migrating VM 202 to node: c02
INFO: Waiting for task (c01:000FAF44:0178B05F:6786EFCA:qmigrate:202) to finish... [ 0:00:00 / 0:10:00 ]
INFO: Waiting for task (c01:000FAF44:0178B05F:6786EFCA:qmigrate:202) to finish... [ 0:00:02 / 0:10:00 ]
INFO: Waiting for task (c01:000FAF44:0178B05F:6786EFCA:qmigrate:202) to finish... [ 0:00:04 / 0:10:00 ]
INFO: Waiting for task (c01:000FAF44:0178B05F:6786EFCA:qmigrate:202) to finish... [ 0:00:06 / 0:10:00 ]
INFO: Waiting for task (c01:000FAF44:0178B05F:6786EFCA:qmigrate:202) to finish... [ 0:00:08 / 0:10:00 ]
INFO: Waiting for task (c01:000FAF44:0178B05F:6786EFCA:qmigrate:202) to finish... [ 0:00:11 / 0:10:00 ]
INFO: VM 202 migrated successfully
INFO: Creating replication jobs for VM 202
INFO: Created replication job VM 202 for node 'c04' with result: True
INFO: Created replication job VM 202 for node 'c05' with result: True
INFO: Created replication job VM 202 for node 'c07' with result: True
INFO: Setup HA for VM 202
INFO: HA Group 'gr-02f-04-05-07' creating with nodes 'c02:100,c04,c05,c07'
INFO: HA Resource for '202' with group 'gr-02f-04-05-07' creating ...
INFO: VM 202 creating resource ...
INFO: Setup Pool for VM 202
INFO: Update pool 'cxx' members with VM '202' ...
INFO: *** Scenario 'CloneTemplateVM-2' completed successfully
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