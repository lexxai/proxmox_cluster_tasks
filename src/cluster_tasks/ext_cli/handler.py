import logging
from asyncio import subprocess as asubprocess
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
            return {"result": None}

        command = input_data.get("command")
        if command is None:
            return {"result": None}

        process = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        result = process.stdout.strip()
        return {"result": result, "status_code": process.returncode}

    async def aprocess(self, input_data: dict | None = None):
        if input_data is None:
            return {"result": None}

        command = input_data.get("command")
        if command is None:
            return {"result": None}

        process = await asubprocess.create_subprocess_shell(
            command, stdout=asubprocess.PIPE, stderr=asubprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                returncode=process.returncode, cmd=command, output=stderr
            )
        result = stdout.decode("utf-8").strip()
        return {"result": result, "status_code": process.returncode}

    def get_version_data(self) -> dict:
        command = self.commands.get("VERSION")
        return {"command": command}

    def get_version(self) -> dict:
        return self.process(self.get_version_data())

    async def aget_version(self) -> dict:
        return await self.aprocess(self.get_version_data())


if __name__ == "__main__":
    logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
    logger.addHandler(logging.StreamHandler())
    logger.info(configuration.get("NODES"))
    # with APIHandler() as api_handler:
    #     logger.info(api_handler.get_version())

    import asyncio

    async def amain():
        async with CLIHandler() as handler:
            logger.info(await handler.aget_version())
            # logger.info(await handler.aget_ha_groups())

    asyncio.run(amain())
