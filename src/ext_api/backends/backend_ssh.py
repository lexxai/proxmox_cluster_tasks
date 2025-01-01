import json
from http.client import responses

import paramiko  # for Sync SSH
import asyncssh  # for Async SSH


from ext_api.backends.backend_cli import (
    ProxmoxCLIBackend,
    ProxmoxAsyncCLIBackend,
    logger,
)


class ProxmoxSSHBaseBackend(ProxmoxCLIBackend):
    def __init__(
        self,
        hostname: str,
        username: str,
        password: str = None,
        key_filename: str = None,
        agent: bool = False,
        port: int = 22,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.hostname = hostname
        self.port = port or 22
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.agent = agent
        self._client = None


class ProxmoxSSHBackend(ProxmoxSSHBaseBackend):

    def connect(self):
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.load_system_host_keys()
        self._client.connect(
            self.hostname,
            port=self.port,
            username=self.username,
            password=self.password or None,
            key_filename=self.key_filename or None,
        )
        if self.agent:
            # use System Agent
            s = self._client.get_transport().open_session()
            paramiko.agent.AgentRequestHandler(s)

    def close(self):
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return True

    def request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        **kwargs,
    ):
        command = self.format_command(endpoint, params, method, data)
        stdin, stdout, stderr = self._client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read()
        error = stderr.read()
        if error:
            logger.error(f"SSH Error: {error.decode()}")
            return {"response": {}, "status_code": exit_status}
        decoded = output.decode().strip()
        try:
            json.loads(decoded)
        except json.JSONDecodeError:
            logger.error(f"SSH Error of decode JSON result: {decoded}")
            return {"response": decoded, "status_code": exit_status}
        return {"response": json.loads(output.decode()), "status_code": exit_status}


class ProxmoxAsyncSSHBackend(ProxmoxAsyncCLIBackend):
    def __init__(self, base_url: str, token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = base_url
        self.token = token

    async def __aenter__(self):
        # Setup async SSH context
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup async SSH context
        pass

    async def async_request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        **kwargs,
    ):
        # Implement async SSH command execution here
        return {"status": "success", "data": "Async SSH result"}
