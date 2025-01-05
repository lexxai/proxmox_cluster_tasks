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
```commandline
python main.py --h         
usage: Proxmox Cluster Tasks [-h] [--debug {true,false,none}] [--sync]

options:
  -h, --help            show this help message and exit
  --debug {true,false,none}
                        Enable or disable debug mode (true, false, none)
  --sync                Run in sync mode, default is async mode
```

[README](../README.md)
