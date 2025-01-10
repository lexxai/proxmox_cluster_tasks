
## Configuration

### `config.toml` File
```toml
DEBUG = false
NODES = []

[API]
TOKEN_ID = ""
TOKEN_SECRET = ""
BASE_URL = ""
ENTRY_POINT = "/api2/json"
VERIFY_SSL = true

[CLI]
ENTRY_POINT = "pvesh"

[SSH]
HOSTNAME = ""
USERNAME = ""
PASSWORD = ""
PORT = 22
AGENT = false
KEY_FILENAME = ""
DISABLE_HOST_KEY_CHECKING  = false
```

### Overriding Configuration with `.env` File
```dotenv
API_TOKEN_ID=user@pam!user_api
API_TOKEN_SECRET=XXXX-YYYY-.....
API_BASE_URL=https://proxmox.local:8006

SSH_HOSTNAME=proxmox.local
SSH_USERNAME=root
```

### Notes:
On the first SSH connection, you might encounter an error indicating that the host is not found in known_hosts or the host key is not trusted. To resolve this, you can either:

- Manually run the SSH client from the console to add the host to your known_hosts file. 
- Alternatively, temporarily set `DISABLE_HOST_KEY_CHECKING` to `true` for the first connection only, and then add the printed host key to your local `known_hosts` file.

  #### Example of console warning:
    ```commandline
    WARNING: SSH host key checking is disabled. This is not recommended for production use.
    INFO: You can add this SSH host key entry, manually to your known_hosts file and enable host key checking again in config:
    '[HOST] ssh-ed25519 AAAA................................................7qcV'
    ```

[README](../README.md)
