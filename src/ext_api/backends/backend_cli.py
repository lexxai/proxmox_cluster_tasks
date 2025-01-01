import asyncio
import logging
import subprocess

from ext_api.backends.backend_abstract import ProxmoxBackend

logger = logging.getLogger("CT.{__name__}")


class ProxmoxCLIBaseBackend(ProxmoxBackend):
    def __init__(
        self,
        entry_point: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.entry_point = entry_point.strip("/")

    def format_command(
        self, endpoint: str, params: dict = None, method: str = None
    ) -> str:
        """Format the full URL for a given endpoint."""
        endpoint = endpoint.strip("/")
        if params:
            endpoint = endpoint.format(**params)
        command = f"{self.entry_point} {method.strip().lower()} {endpoint.lstrip('/')}"
        logger.debug("Formatted command: %s", command)
        return command


class ProxmoxCLIBackend(ProxmoxCLIBaseBackend):

    def request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        *args,
        **kwargs,
    ):
        command = self.format_command(endpoint, params, method)

        try:
            process = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            result = process.stdout.strip()
            return {"response": result, "status_code": process.returncode}
        except subprocess.CalledProcessError as e:
            return {"response": None, "status_code": e.returncode}


class ProxmoxAsyncCLIBackend(ProxmoxCLIBaseBackend):

    async def async_request(
        self,
        method: str = None,
        endpoint: str = None,
        params: dict = None,
        data: dict = None,
        *args,
        **kwargs,
    ):
        command = self.format_command(endpoint, params, method)

        if command is None:
            return {"response": None, "status_code": -1}
        try:
            process = await asyncio.create_subprocess_shell(
                command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    returncode=process.returncode, cmd=command, output=stderr
                )
            result = stdout.decode("utf-8").strip()
            return {"response": result, "status_code": process.returncode}
        except subprocess.CalledProcessError as e:
            return {"response": None, "status_code": e.returncode}
