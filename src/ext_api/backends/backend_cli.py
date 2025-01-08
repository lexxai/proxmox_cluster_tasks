import asyncio
import logging
import shlex
import subprocess

from ext_api.backends.backend_abstract import ProxmoxBackend

logger = logging.getLogger("CT.{__name__}")


class ProxmoxCLIBaseBackend(ProxmoxBackend):
    METHOD_MAP = {
        "post": "create",
        "put": "set",
    }

    def __init__(
        self,
        entry_point: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.entry_point = entry_point.strip("/")

    def format_command(
        self,
        endpoint: str,
        params: dict = None,
        method: str = None,
        data: dict = None,
        endpoint_params: dict = None,
    ) -> str:
        if endpoint is None:
            raise ValueError("CLI backend: Endpoint is required")
        """Format the full URL for a given endpoint."""
        endpoint = endpoint.rstrip("/")
        method = method.strip().lower()
        method = self.METHOD_MAP.get(method, method)
        if endpoint_params:
            endpoint = endpoint.format(**endpoint_params)
        command = [self.entry_point, method, endpoint]
        if params:
            command.extend([f"--{k}={shlex.quote(str(v))}" for k, v in params.items()])
        if data:
            command.extend([f"--{k}={shlex.quote(str(v))}" for k, v in data.items()])
        command.append("--output-format=json")
        command = " ".join(command)
        logger.debug("Formatted command: %s", command)
        return command


class ProxmoxCLIBackend(ProxmoxCLIBaseBackend):

    def request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        endpoint_params: dict = None,
        *args,
        **kwargs,
    ):
        command = self.format_command(endpoint, params, method, data, endpoint_params)
        if command is None:
            return {"response": None, "status_code": -1, "success": False}
        try:
            process = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            result = process.stdout.strip()
            success = process.returncode == 0
            return {
                "response": {"data": result},
                "status_code": process.returncode,
                "success": success,
            }
        except subprocess.CalledProcessError as e:
            return {"response": None, "status_code": e.returncode, "success": False}


class ProxmoxAsyncCLIBackend(ProxmoxCLIBaseBackend):

    async def async_request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        endpoint_params: dict = None,
        *args,
        **kwargs,
    ):
        command = self.format_command(endpoint, params, method, data, endpoint_params)

        if command is None:
            return {"response": None, "status_code": -1, "success": False}
        try:
            process = await asyncio.create_subprocess_shell(
                command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    returncode=process.returncode, cmd=command, output=stderr
                )
            if hasattr(stdout, "decode"):
                stdout = stdout.decode("utf-8")
            result = stdout.strip() if isinstance(stdout, str) else None
            success = process.returncode == 0
            return {
                "response": {"data": result},
                "status_code": process.returncode,
                "success": success,
            }
        except subprocess.CalledProcessError as e:
            return {"response": None, "status_code": e.returncode, "success": False}
