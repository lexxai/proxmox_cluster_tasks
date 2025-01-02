import asyncio
import logging

from cluster_tasks.configure_logging import config_logger
from cluster_tasks.resources.resources import Resources, AsyncResources
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI

logger = logging.getLogger("CT")
config_logger(logger)


def main():
    register_backends(["https"])
    ext_api = ProxmoxAPI(backend_name="https", backend_type="sync")
    with ext_api as api:
        resources = Resources(api)
        logger.info(resources.get_version())
        logger.info(resources.cluster.ha.get_groups())


async def async_main():
    register_backends(["https"])
    ext_api = ProxmoxAPI(backend_name="https", backend_type="async")
    async with ext_api as api:
        resources = AsyncResources(api)
        logger.info(await resources.get_version())
        logger.info(await resources.cluster.ha.get_groups())


if __name__ == "__main__":
    try:
        main()
        asyncio.run(async_main())
    except Exception as e:
        logger.error(f"MAIN: {e}")
