import asyncio
import logging

from cluster_tasks.config import configuration
from cluster_tasks.ext_api.handler import APIHandler


logger = logging.getLogger(f"CT.{__name__}")

logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
logger.addHandler(logging.StreamHandler())
logger.info(configuration.get("NODES"))


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
                data = sorted(data.items())
        else:
            data = None
        logger.info(f"Node: {node}, Result: {data}")


async def async_main():
    async with APIHandler() as api_handler:
        logger.info(await api_handler.aget_version())
        await debug_get_ha_groups(api_handler)
        await debug_get_status(api_handler)


if __name__ == "__main__":
    asyncio.run(async_main())
