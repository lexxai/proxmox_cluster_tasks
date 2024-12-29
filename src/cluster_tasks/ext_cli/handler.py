from cluster_tasks.config import configuration
from cluster_tasks.ext_abs.base import AbstractHandler


class CLIHandler(AbstractHandler):
    """Concrete implementation for handling CLI logic."""

    def process(self, input_data: dict | None = None):
        print(f"Processing CLI data: {input_data}")
        # CLI-specific logic here
        return {"result": f"CLI processed {input_data}"}

    def get_version(self):
        command = configuration.get("cli_commands.version")
        return self.process(command)
