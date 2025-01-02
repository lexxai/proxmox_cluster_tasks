import asyncio
import logging

from cluster_tasks.configure_logging import config_logger
from cluster_tasks.tasks.proxmoxtasks import ProxmoxTasks, ProxmoxAsyncTasks
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI

logger = logging.getLogger("CT")
config_logger(logger)


def main():
    register_backends(["https"])
    ext_api = ProxmoxAPI(backend_name="https", backend_type="sync")
    with ext_api as api:
        task = ProxmoxTasks(api)
        logger.info(task.get_version())
        logger.info(task.cluster.ha.get_groups())


async def async_main():
    register_backends(["https"])
    ext_api = ProxmoxAPI(backend_name="https", backend_type="async")
    async with ext_api as api:
        task = ProxmoxAsyncTasks(api)
        logger.info(await task.get_version())
        logger.info(await task.cluster.ha.get_groups())
        # response = await api.async_request("get", "version")
        # logger.info(response)


if __name__ == "__main__":
    try:
        main()
        asyncio.run(async_main())
    except Exception as e:
        logger.error(f"MAIN: {e}")
