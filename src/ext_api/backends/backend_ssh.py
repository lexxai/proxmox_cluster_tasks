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
        one_time = False
        if not self._client:
            self.connect()
            logger.warning(
                "SSH client session is not initialized. Use 'with' context to start a session. Creating onetime client instance."
            )
            one_time = True
        command = self.format_command(endpoint, params, method, data)
        try:
            stdin, stdout, stderr = self._client.exec_command(command)
        except paramiko.ssh_exception.SSHException as e:
            logger.error(f"SSH Error: {e}")
            return {"response": {}, "status_code": 1}
        finally:
            if one_time:
                self.close()
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read()
        error = stderr.read()
        success = exit_status == 0
        if error:
            logger.error(f"SSH Error: {error.decode()}")
            return {"response": {}, "status_code": exit_status, "success": success}
        decoded = output.decode().strip()
        try:
            json.loads(decoded)
        except json.JSONDecodeError:
            logger.error(f"SSH Error of decode JSON result: {decoded}")
            return {
                "response": {"data": decoded},
                "status_code": exit_status,
                "success": success,
            }
        return {
            "response": {"data": json.loads(output.decode())},
            "status_code": exit_status,
            "success": success,
        }


class ProxmoxAsyncSSHBackend(ProxmoxSSHBaseBackend):

    async def connect(self):
        params = {
            "host": self.hostname,
            "username": self.username,
            "password": self.password,
            "port": self.port,
        }
        if self.key_filename:
            params["client_keys"] = [self.key_filename]

        self._client = await asyncssh.connect(**params)

    async def close(self):
        if self._client:
            self._client.close()
            await self._client.wait_closed()
            self._client = None

    async def __aenter__(self):
        # Setup async SSH context
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return True

    async def async_request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        **kwargs,
    ):
        # Implement async SSH command execution here
        one_time = False
        if not self._client:
            await self.connect()
            logger.warning(
                "Async SSH client session is not initialized. Use 'with' context to start a session. Creating onetime client instance."
            )
            one_time = True

        command = self.format_command(endpoint, params, method, data)
        try:
            result = await self._client.run(command, check=True)
        except asyncssh.ProcessError as e:
            logger.error(f"Async SSH Error: {e}")
            return {"response": {}, "status_code": e.exit_status}
        finally:
            if one_time:
                await self.close()
        output, error, exit_status = result.stdout, result.stderr, result.exit_status
        success = exit_status == 0
        if error:
            logger.error(f"SSH Error: {error.decode()}")
            return {"response": {}, "status_code": exit_status, "success": success}
        decoded = output.strip()
        try:
            json.loads(decoded)
        except json.JSONDecodeError:
            logger.error(f"SSH Error of decode JSON result: {decoded}")
            return {
                "response": {"data": decoded},
                "status_code": exit_status,
                "success": success,
            }
        return {
            "response": {"data": json.loads(decoded)},
            "status_code": exit_status,
            "success": success,
        }
