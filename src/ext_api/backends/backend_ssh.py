import json
import logging

logger = logging.getLogger(f"CT.{__name__}")

try:
    import paramiko  # for Sync SSH
except ImportError as e:
    logger.error(f"SSH Backend require load module: {e}")
    exit(1)
try:
    import asyncssh  # for Async SSH
except ImportError as e:
    logger.error(f"Async SSH Backend require load module: {e}")
    exit(1)


from ext_api.backends.backend_cli import (
    ProxmoxCLIBaseBackend,
)


class ProxmoxSSHBaseBackend(ProxmoxCLIBaseBackend):
    def __init__(
        self,
        hostname: str,
        username: str,
        password: str = None,
        key_filename: str = None,
        agent: bool = False,
        disable_host_key_checking: bool = False,
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
        self.disable_host_key_checking: bool = disable_host_key_checking
        self._client: (
            paramiko.client.SSHClient | asyncssh.SSHClientConnection | None
        ) = None
        if disable_host_key_checking:
            logger.warning(
                "SSH host key checking is disabled. This is not recommended for production use."
            )

    @staticmethod
    def result_analyze(output, error, exit_status) -> dict:
        success = exit_status == 0
        if error:
            if hasattr(error, "decode"):
                error = error.decode().strip()
            logger.debug(f"SSH Error: {repr(error)}")
        if hasattr(output, "decode"):
            output = output.decode()
        decoded = output.strip() if isinstance(output, str) else output
        if not decoded:
            return {
                "response": {"data": {}},
                "status_code": exit_status,
                "success": success,
                "error": error,
            }
        try:
            json.loads(decoded)
        except json.JSONDecodeError:
            logger.debug(
                f"SSH Error of decode JSON result: {decoded.splitlines()[-1]}..."
            )
            return {
                "response": {"data": decoded.splitlines()[-1]},
                "status_code": exit_status,
                "success": success,
            }
        return {
            "response": {"data": json.loads(decoded)},
            "status_code": exit_status,
            "success": success,
        }

    @property
    def client(self):
        return self._client


class ProxmoxSSHBackend(ProxmoxSSHBaseBackend):

    def connect(self):
        self._client = paramiko.SSHClient()
        if self.disable_host_key_checking:
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._client.preferred_keys = ["ssh-ed25519", "ssh-rsa"]
        self._client.load_system_host_keys()
        self._client.connect(
            self.hostname,
            port=self.port,
            username=self.username,
            password=self.password or None,
            key_filename=self.key_filename or None,
        )

        self.show_host_key(self._client)

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
        endpoint_params: dict = None,
        **kwargs,
    ):
        one_time = False
        if not self._client:
            self.connect()
            logger.warning(
                "SSH client session is not initialized. Use 'with' context to start a session. Creating onetime client instance."
            )
            one_time = True
        command = self.format_command(endpoint, params, method, data, endpoint_params)
        try:
            if not command:
                raise ValueError("SSH command is empty")
            stdin, stdout, stderr = self._client.exec_command(command)
        except Exception as e:
            logger.debug(f"SSH Error: {e}")
            return {"response": {}, "status_code": 1, "error": str(e), "success": False}
        finally:
            if one_time:
                self.close()
        exit_status = stdout.channel.recv_exit_status()
        return self.result_analyze(stdout.read(), stderr.read(), exit_status)

    def show_host_key(self, client):
        if self.disable_host_key_checking:
            # Retrieve the server's host key
            host_key = client.get_transport().get_remote_server_key()
            key_type = host_key.get_name()
            key_data = host_key.get_base64()
            # Format the host key entry
            host_key_entry = f"{self.hostname} {key_type} {key_data}"
            logger.info(
                f"You can add this SSH host key entry, manually to your known_hosts file and enable host key checking again in config:\n'{host_key_entry}'"
            )


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

        if self.disable_host_key_checking:
            params["known_hosts"] = None
            params["server_host_key_algs"] = ["ssh-ed25519", "ssh-rsa"]

        self._client = await asyncssh.connect(**params)

        self.show_host_key(self._client)

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
        endpoint_params: dict = None,
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

        command = self.format_command(endpoint, params, method, data, endpoint_params)
        try:
            result = await self._client.run(command, check=True)
        except asyncssh.ProcessError as e:
            logger.debug(f"Async SSH Error: {e}")
            return {"response": {}, "status_code": e.exit_status, "error": e.stderr}
        finally:
            if one_time:
                await self.close()
        return self.result_analyze(result.stdout, result.stderr, result.exit_status)

    def show_host_key(self, client):
        if self.disable_host_key_checking:
            host_key = client.get_server_host_key()
            exported_key = host_key.export_public_key()
            if isinstance(exported_key, bytes):
                exported_key = exported_key.decode("utf-8").strip()
            host_key_entry = f"{self.hostname} {exported_key}"
            logger.info(
                f"You can add this SSH host key entry, manually to your known_hosts file and enable host key checking again in config:\n'{host_key_entry}'"
            )
