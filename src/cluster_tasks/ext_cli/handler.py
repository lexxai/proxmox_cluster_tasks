import logging
import subprocess

from cluster_tasks.config import configuration
from cluster_tasks.ext_abs.base import AbstractHandler

logger = logging.getLogger(f"CT.{__name__}")


class CLIHandler(AbstractHandler):
    """Concrete implementation for handling CLI logic."""

    def __init__(self):
        super().__init__()
        self.commands: dict = configuration.get("CLI_COMMANDS")

    def process(self, input_data: dict | None = None):
        if input_data is None:
            return {"result": None, "status_code": -1}
        command = input_data.get("command")
        if command is None:
            return {"result": None, "status_code": -1}
        try:
            process = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            result = process.stdout.strip()
            return {"result": result, "status_code": process.returncode}
        except subprocess.CalledProcessError as e:
            return {"result": None, "status_code": e.returncode}

    async def aprocess(self, input_data: dict | None = None):
        if input_data is None:
            return {"result": None, "status_code": -1}
        command = input_data.get("command")
        if command is None:
            return {"result": None, "status_code": -1}
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
            return {"result": result, "status_code": process.returncode}
        except subprocess.CalledProcessError as e:
            return {"result": None, "status_code": e.returncode}

    # VERSION
    def get_version_data(self) -> dict:
        command = self.commands.get("VERSION")
        return {"command": command}

    # HA_GROUPS
    # GET HA_GROUPS
    def get_ha_groups_data(self) -> dict:
        command = self.commands.get("HA_GROUPS")
        return {"command": command}

    # STATUS
    # GET STATUS
    def get_status_data(self, target_node: str) -> dict:
        command = self.commands.get("STATUS")
        command = command.format(TARGETNODE=target_node)
        input_data = {
            "command": command,
        }
        return input_data


if __name__ == "__main__":
    logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
    logger.addHandler(logging.StreamHandler())
    logger.info(configuration.get("NODES"))
    # with APIHandler() as api_handler:
    #     logger.info(api_handler.get_version())

    import asyncio

    async def ping():
        for _ in range(10):
            print("Ping ...")
            await asyncio.sleep(1)

    async def amain():
        # test for blocking
        asyncio.create_task(ping())
        async with CLIHandler() as handler:
            logger.info(await handler.aget_version())
            logger.info(await handler.aget_ha_groups())

    asyncio.run(amain())
