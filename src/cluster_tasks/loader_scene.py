import importlib

from ext_api.proxmox_api import ProxmoxAPI


class ScenarioFactory:
    base_module = "scenarios"
    prefix_class = "Scenario"
    suffix_file = {"sync": "_sync", "async": "_async"}

    @staticmethod
    def convert_to_class_name(file_name: str) -> str:
        """Convert a file name (snake_case) to a class name (PascalCase)."""
        words = file_name.replace("_", " ").split()
        return "".join(word.capitalize() for word in words)

    @classmethod
    def load_class(cls, module_name: str, class_name: str):
        """Dynamically load a class from a given module."""
        module = importlib.import_module(module_name)  # Import the module
        return getattr(module, class_name)

    @classmethod
    def create_scenario(
        cls, scenario_file: str, config: dict = None, run_type: str = "sync"
    ):
        # Dynamically load the scenario class based on the name
        scenario_file = f"{scenario_file}{cls.suffix_file.get(run_type)}"
        module_name = f"{cls.base_module}.{scenario_file}"
        scenario_name = cls.convert_to_class_name(scenario_file)

        scenario_class = cls.load_class(
            module_name, f"{cls.prefix_class}{scenario_name}"
        )

        scenario_instance = scenario_class()
        scenario_instance.configure(config)
        return scenario_instance
