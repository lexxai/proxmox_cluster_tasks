# proxmox_cluster_tasks
proxmox cluster automatic tasks helper

## API Reference
- Usage of Proxmox VE API : https://pve.proxmox.com/wiki/Proxmox_VE_API
- Proxmox VE API Viewer: https://pve.proxmox.com/pve-docs/api-viewer


## Debug
### Debug API
<details>
<summary>src/cluster_tasks/debug_api.py</summary>

```commandline
['c01', 'c02', 'c03', 'c04', 'c05', 'c06', 'c07', 'c08']
{'result': {'data': {'release': '8.3', 'version': '8.3.2', 'repoid': '......'}}, 'status_code': 200}
Waiting for results... of aget_ha_groups
Group: gr-02-03f-04 - c03:50,c02:40,c04:30
Group: gr-03f-04-05 - c05:30,c03:50,c04:40
Group: gr-01f-02-03 - c01:50,c03:30,c02:40
Group: gr-01-02-03f - c01:30,c03:50,c02:40
Group: gr-04f-05-06 - c04:50,c05:40,c06:30
Group: gr-02f-03-04 - c02:50,c03:40,c04:30
Group: gr-01-02f-03 - c01:40,c02:50,c03:30
Group: gr-05-06-07f - c07:50,c06:40,c05:30
Group: gr-03-04f-05 - c04:50,c05:30,c03:40
Group: gr-05-06f-07 - c05:40,c07:30,c06:50
Group: gr-06-07-08f - c06:30,c08:50,c07:40
Group: gr-04-05-06f - c05:40,c06:50,c04:30
Group: gr-06f-07-08 - c06:50,c08:30,c07:40
Group: gr-03-04-05f - c04:40,c05:50,c03:30
Group: gr-04-05f-06 - c05:50,c04:40,c06:30
Group: gr-05f-06-07 - c05:50,c06:40,c07:30
Group: gr-06-07f-08 - c07:50,c06:40,c08:30
Group: gr-02-03-04f - c04:50,c02:30,c03:40
Waiting for results... of tasks: 8
Node: c01, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '2 days, 11:05:50'}
Node: c02, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '2 days, 11:05:32'}
Node: c03, Result: {}
Node: c04, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '2 days, 11:05:45'}
Node: c05, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '2 days, 11:05:40'}
Node: c06, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '62.85 GB', 'uptime': '0:04:22'}
Node: c07, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '125.85 GB', 'uptime': '2 days, 11:05:37'}
Node: c08, Result: {'kversion': 'Linux 6.8.12-5-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-5 (2024-12-03T10:26Z)', 'cpus': 24, 'cpus_model': 'Intel(R) Xeon(R) CPU E5-2643 v2 @ 3.50GHz', 'memory_total': '125.85 GB', 'uptime': '2 days, 11:05:32'}
```
</details>
