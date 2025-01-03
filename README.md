# proxmox_cluster_tasks
proxmox cluster automatic tasks helper

## API Reference
- Usage of Proxmox VE API : https://pve.proxmox.com/wiki/Proxmox_VE_API
- Proxmox VE API Viewer: https://pve.proxmox.com/pve-docs/api-viewer


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
