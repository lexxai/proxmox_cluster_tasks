import asyncio
import json
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

    @staticmethod
    def result_analyze(output, error, exit_status) -> dict:
        success = exit_status == 0
        if error:
            if hasattr(error, "decode"):
                error = output.decode().strip()
            logger.debug(f"CLI Error: {repr(error)}")
        if hasattr(output, "decode"):
            output = output.decode("utf-8")
        decoded = output.strip() if isinstance(output, str) else None
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
                f"CLI Error of decode JSON result: {decoded.splitlines()[-1]}..."
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
            output = process.stdout
            error = process.stderr
            exit_status = process.returncode
            return self.result_analyze(output, error, exit_status)
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
            output, error = await process.communicate()
            exit_status = process.returncode
            if exit_status != 0:
                raise subprocess.CalledProcessError(
                    returncode=exit_status, cmd=command, output=output
                )
            return self.result_analyze(output, error, exit_status)
        except subprocess.CalledProcessError as e:
            return {"response": None, "status_code": e.returncode, "success": False}
