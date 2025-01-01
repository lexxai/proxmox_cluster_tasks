import json
import logging

import paramiko  # for Sync SSH
import asyncssh  # for Async SSH


from ext_api.backends.backend_cli import (
    ProxmoxCLIBaseBackend,
)

logger = logging.getLogger(f"CT.{__name__}")


class ProxmoxSSHBaseBackend(ProxmoxCLIBaseBackend):
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
        self.hostname: str = hostname
        self.port: int = port or 22
        self.username: str = username
        self.password: str = password
        self.key_filename: str = key_filename
        self.agent: bool = agent
        self._client: (
            paramiko.client.SSHClient | asyncssh.SSHClientConnection | None
        ) = None


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


class ProxmoxAsyncSSHBackend(ProxmoxSSHBaseBackend):

    async def __aenter__(self):
        # Setup async SSH context
        params = {
            "host": self.hostname,
            "username": self.username,
            "password": self.password,
            "port": self.port,
        }
        if self.key_filename:
            params["client_keys"] = [self.key_filename]

        self._client = await asyncssh.connect(**params)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            self._client.close()
            await self._client.wait_closed()
            self._client = None

    async def async_request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        **kwargs,
    ):
        # Implement async SSH command execution here
        if not self._client:
            raise RuntimeError("Async SSH Connection not opened")

        command = self.format_command(endpoint, params, method, data)
        try:
            result = await self._client.run(command, check=True)
        except asyncssh.ProcessError as e:
            logger.error(f"Async SSH Error: {e}")
            return {"response": {}, "status_code": e.exit_status}
        output, error, exit_status = result.stdout, result.stderr, result.exit_status
        if error:
            logger.error(f"SSH Error: {error.decode()}")
            return {"response": {}, "status_code": exit_status}
        decoded = output.strip()
        try:
            json.loads(decoded)
        except json.JSONDecodeError:
            logger.error(f"SSH Error of decode JSON result: {decoded}")
            return {"response": decoded, "status_code": exit_status}
        return {"response": json.loads(decoded), "status_code": exit_status}
