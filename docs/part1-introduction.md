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


[README](../README.md)
