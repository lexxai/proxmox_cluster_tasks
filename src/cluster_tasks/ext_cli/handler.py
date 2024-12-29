from cluster_tasks.config import configuration
from cluster_tasks.ext_abs.base import AbstractHandler


class CLIHandler(AbstractHandler):
    """Concrete implementation for handling CLI logic."""

    def __init__(self):
        super().__init__()
        self.commands: dict = configuration.get("CLI_COMMANDS")

    def process(self, input_data: dict | None = None):
        # print(f"Processing CLI data: {input_data}")
        # CLI-specific logic here
        return {"result": f"CLI processed {input_data}"}

    async def aprocess(self, input_data: dict | None = None):
        # print(f"Processing CLI data: {input_data}")
        # CLI-specific logic here
        return {"result": f"CLI processed {input_data}"}

    def get_version_data(self) -> dict:
        command = self.commands.get("VERSION")
        return {"command": command}

    def get_version(self) -> dict:
        return self.process(self.get_version_data())

    async def aget_version(self) -> dict:
        return await self.aprocess(self.get_version_data())
