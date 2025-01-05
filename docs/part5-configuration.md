
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
```

### Overriding Configuration with `.env` File
```dotenv
API_TOKEN_ID=user@pam!user_api
API_TOKEN_SECRET=XXXX-YYYY-.....
API_BASE_URL=https://proxmox.local:8006

SSH_HOSTNAME=proxmox.local
SSH_USERNAME=root
```
