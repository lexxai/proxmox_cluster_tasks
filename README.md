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

## Documentation

- [API Reference](docs/part2-api-reference.md)
- [Setup Instructions](docs/part3-setup.md)
- [Scenarios](docs/part6-scenarios.md)
- NodeTasks Class
- ProxmoxAPI Class
  - [Examples](docs/part4-1-proxmoxapi-examples.md)
  - [Advanced Concurrent Usage and Low-Level API Requests](docs/part4-2-advanced-examples.md)
  - [Filtering results](docs/part4-3-proxmoxapi-filtering.md)
  - [Debug Results](docs/part4-4-debug.md)
- [Configuration](docs/part5-configuration.md)



## Acknowledgments

Special thanks to the [proxmoxer](https://github.com/proxmoxer/proxmoxer) project for providing inspiration and solutions that influenced the development of this library.

