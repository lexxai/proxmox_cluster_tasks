import asyncio
import logging
from datetime import timedelta

from cluster_tasks.config import configuration
from cluster_tasks.ext_api.handler import APIHandler


logger = logging.getLogger(f"CT")

logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
logger.addHandler(logging.StreamHandler())
logger.info(configuration.get("NODES"))


def human_readable_size(size_in_bytes):
    """
    Converts a size in bytes to a human-readable format.

    Args:
        size_in_bytes (int): Size in bytes.

    Returns:
        str: Human-readable size.
    """
    if size_in_bytes is None:
        return "Unknown"

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(size_in_bytes)
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


async def debug_get_ha_groups(api_handler: APIHandler):
    logger.info("Waiting for results... of aget_ha_groups")
    results = await api_handler.aget_ha_groups()
    # logger.info(results)
    if results:
        data = results.get("result", {})
        if data:
            data = data.get("data", [])
        else:
            data = []
        for group in data:
            group_name = group.get("group")
            group_nodes = group.get("nodes")

            logger.info(f"Group: {group_name} - {group_nodes}")


async def debug_get_status(api_handler: APIHandler):
    nodes = configuration.get("NODES", [])  # Extract nodes to a list
    tasks = []
    for node in nodes:
        # logger.info(node)
        tasks.append(api_handler.aget_status(node))
    logger.info("Waiting for results... of tasks: %s", len(tasks))
    results = await asyncio.gather(*tasks)
    # logger.info(len(results))
    for node, result in zip(nodes, results):
        if result is not None:
            data = result.get("result", {})
            if data:
                data = data.get("data", {})
                data = {
                    "kversion": data.get("kversion", {}),
                    "cpus": data.get("cpuinfo", {}).get("cpus", {}),
                    "cpus_model": data.get("cpuinfo", {}).get("model", {}),
                    "memory_total": human_readable_size(
                        data.get("memory", {}).get("total", 0)
                    ),
                    "uptime": str(timedelta(seconds=data.get("uptime", 0))),
                }
                # data = data.get("boot-info", {})
        else:
            data = None
        logger.info(f"Node: {node}, Result: {data}")


async def debug_create_ha_group(handler: APIHandler):
    result = await handler.acreate_ha_group("test-gr-02-03f-04", ["c03", "c02", "c04"])
    logger.info(result)


async def async_main():
    async with APIHandler() as handler:
        try:
            logger.info(await handler.aget_version())
            await debug_get_ha_groups(handler)
            await debug_create_ha_group(handler)
            await debug_get_ha_groups(handler)

            # await debug_get_status(handler)
        except Exception as e:
            logger.error(f"ERROR async_main: {e}")


if __name__ == "__main__":
    asyncio.run(async_main())
