import asyncio
import logging
from pathlib import Path

from cluster_tasks.configure_logging import config_logger
from cluster_tasks.tasks.proxmox_tasks_async import ProxmoxTasksAsync
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI

logger = logging.getLogger(f"CT.{__name__}")


async def debug_replication(proxmox_tasks):
    vm_id = 202
    target_node = "c07"
    data = {"schedule": "*/30", "comment": "repl 1"}
    # data = None
    logger.info(
        await proxmox_tasks.create_replication_job(vm_id, target_node, data=data)
    )
    logger.info(await proxmox_tasks.create_replication_job(vm_id, "c04", data=data))
    logger.info("Sleep 5")
    await asyncio.sleep(5)
    # target_node = None
    # logger.info(
    #     await proxmox_tasks.remove_replication_job(vm_id, target_node=None, wait=True)
    # )


async def debug_ha_groups(proxmox_tasks):
    # logger.info(await proxmox_tasks.ha_groups_get())
    logger.info(
        await proxmox_tasks.ha_group_create(
            "test_group_name1", "c01,c02,c96", overwrite=False
        )
    )
    logger.info(await proxmox_tasks.vm_status_set(202, "c02", "stop"))
    # logger.info(await proxmox_tasks.ha_groups_get())
    # logger.info(await proxmox_tasks.ha_group_delete("test_group_name"))


async def debug_ha_resources(proxmox_tasks):
    logger.info(
        await proxmox_tasks.ha_resources_get(vid_id=102, return_group_only=False)
    )


async def async_main():
    register_backends()
    async with ProxmoxAPI(backend_type="async") as api:
        try:
            proxmox_tasks = ProxmoxTasksAsync(api=api)
            # await debug_replication(proxmox_tasks)
            # await debug_ha_groups(proxmox_tasks)
            await debug_ha_resources(proxmox_tasks)
        except Exception as e:
            logger.error(f"ERROR async_main: {e}")


if __name__ == "__main__":
    logger = logging.getLogger("CT")
    config_logger(logger, debug=True)
    try:
        asyncio.run(async_main())
    except Exception as e:
        logger.error(e)
