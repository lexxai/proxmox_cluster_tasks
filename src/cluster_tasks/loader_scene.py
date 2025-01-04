import importlib

from ext_api.proxmox_api import ProxmoxAPI


class ScenarioFactory:
    base_module = "scenarios"
    prefix_file = "scenario_"
    prefix_class = "Scenario"

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
    def create_scenario(cls, scenario_file: str, api: ProxmoxAPI, config: dict = None):
        # Dynamically load the scenario class based on the name
        scenario_file = f"{cls.prefix_file}{scenario_file}"
        module_name = f"{cls.base_module}.{scenario_file}"
        scenario_name = cls.convert_to_class_name(scenario_file)

        scenario_class = cls.load_class(module_name, scenario_name)

        scenario_instance = scenario_class(api)
        scenario_instance.configure(config)
        return scenario_instance
