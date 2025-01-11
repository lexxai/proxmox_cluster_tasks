import logging
from pathlib import Path

from cluster_tasks.configure_logging import config_logger
from cluster_tasks.tasks.proxmox_tasks_sync import ProxmoxTasksSync
from config.config import ConfigLoader
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI
from loader_scene import ScenarioFactory

logger = logging.getLogger(f"CT.{__name__}")


def sanitize_config(config):
    sensitive_keys = ["API.TOKEN_SECRET", "API.TOKEN_ID"]
    sanitized_config = {
        k: (v if k not in sensitive_keys else "****") for k, v in config.items()
    }
    return sanitized_config


def main():
    config_file = Path(__file__).parent / "scenarios_configs.yaml"
    scenarios_config = ConfigLoader(file_path=config_file)
    # Iterate over the scenarios and run them
    logger.debug(f"Scenarios config: {scenarios_config}")
    backend_name = scenarios_config.get("API.backend", "https")
    register_backends(backend_name)
    ext_api = ProxmoxAPI(backend_name=backend_name, backend_type="sync")
    try:
        with ext_api as api:
            node_tasks = ProxmoxTasksSync(api=api)
            for v in scenarios_config.get("Scenarios").values():
                config = v.get("config")
                # sanitized_config = sanitize_config(config)
                # logger.debug(f"Config: {sanitized_config}")
                node = config.get("node")
                source_vm_id = config.get("source_vm_id")
                destination_vm_id = config.get("destination_vm_id")
                network = config.get("network", {})
                ip = network.get("ip")
                gw = network.get("gw")
                increase_ip = network.get("increase_ip")
                decrease_ip = network.get("decrease_ip")
                full = config.get("full", 1)
                logger.info(
                    api.nodes(node)
                    .qemu(destination_vm_id)
                    .config.get(filter_keys="ipconfig0")
                )

                setconfig = {
                    "ip": ip,
                    "gw": gw,
                    "increase_ip": increase_ip,
                    "decrease_ip": decrease_ip,
                    "full": full,
                }
                result = node_tasks.vm_config_network_set(
                    node, destination_vm_id, config=setconfig
                )
                # logger.info(f"VM configuration network set result: {result}")
                logger.info(
                    api.nodes(node)
                    .qemu(destination_vm_id)
                    .config.get(filter_keys="ipconfig0")
                )

    except Exception as e:
        logger.error(f"MAIN: {e}")


if __name__ == "__main__":
    logger = logging.getLogger("CT")
    config_logger(logger)
    main()
