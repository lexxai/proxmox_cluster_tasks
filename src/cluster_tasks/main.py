import asyncio
import logging

from cluster_tasks.configure_logging import config_logger
from cluster_tasks.resources.resources import Resources, AsyncResources
from config.config import configuration
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI

logger = logging.getLogger("CT")
config_logger(logger)


def main():
    register_backends(["https"])
    ext_api = ProxmoxAPI(backend_name="https", backend_type="sync")
    with ext_api as api:
        # resources = Resources(api)
        logger.info(api.version.get(filter_keys="version"))
        logger.info(api.cluster.ha.groups.get(filter_keys=["group", "nodes"]))
        node = configuration.get("NODES")[0]
        # logger.info(api.nodes(node).status.get(filter_keys=["kversion", "uptime"]))
        logger.info(api.nodes(node).status.get(filter_keys="current-kernel.release"))


async def async_main():
    register_backends(["https"])
    ext_api = ProxmoxAPI(backend_name="https", backend_type="async")
    async with ext_api as api:
        # resources = AsyncResources(api)
        logger.info(await api.version.get(filter_keys="version"))
        logger.info(await api.cluster.ha.groups.get(filter_keys=["group", "nodes"]))
        node = configuration.get("NODES")[0]
        logger.info(
            await api.nodes(node).status.get(filter_keys=["kversion", "uptime"])
        )
        logger.info(
            await api.nodes(node).status.get(filter_keys="current-kernel.release")
        )


if __name__ == "__main__":
    try:
        main()
        asyncio.run(async_main())
    except ValueError as e:
        logger.error(f"MAIN: {e}")
