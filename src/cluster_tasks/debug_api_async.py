import asyncio
import logging
from datetime import timedelta
from importlib.metadata import version

from cluster_tasks.configure_logging import config_logger
from config.config import configuration
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI


logger = logging.getLogger(f"CT")
logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
config_logger(logger)

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


async def debug_get_ha_groups(api: ProxmoxAPI):
    logger.info("Waiting for results... of aget_ha_groups")
    groups = await api.cluster.ha.groups.get(filter_keys=["group", "nodes"])
    # logger.info(results)
    if groups:
        logger.info(f"Total groups in cluster: {len(groups)}")
        for i, group in enumerate(groups, start=1):
            group_name = group.get("group")
            group_nodes = group.get("nodes")
            logger.info(f"{i}: Group: {group_name} Nods: {group_nodes}")


async def debug_get_node_status_sequenced(api: ProxmoxAPI):
    nodes: list[dict] = await api.nodes.get(filter_keys=["node", "status"])
    if nodes:
        nodes = sorted([n.get("node") for n in nodes if n.get("status") == "online"])
        logger.info(nodes)
    # nodes = configuration.get("NODES", [])  # Extract nodes to a list
    tasks = []
    results = []
    for node in nodes:
        logger.info(node)
        # tasks.append(api.nodes(node).status.get())
        results.append(
            await api.nodes(node).status.get(
                filter_keys=["kversion", "cpuinfo", "memory.total", "uptime"]
            )
        )
    logger.info("Waiting for results... of resources: %s", len(tasks))
    # results = await asyncio.gather(*tasks)
    # logger.info(len(results))
    for node, data in zip(nodes, results):
        # logger.debug(data)
        if data is not None:
            data = {
                "kversion": data.get("kversion", {}),
                "cpus": data.get("cpuinfo", {}).get("cpus", {}),
                "cpus_model": data.get("cpuinfo", {}).get("model", {}),
                "memory_total": human_readable_size(data.get("memory.total")),
                "uptime": str(timedelta(seconds=data.get("uptime", 0))),
            }
            # data = data.get("boot-info", {})
        else:
            data = None
        logger.info(f"Node: {node}, Result: {data}")


async def debug_get_node_status_parallel(api: ProxmoxAPI):
    nodes: list[dict] = await api.nodes.get(filter_keys=["node", "status"])
    if nodes:
        nodes = sorted([n.get("node") for n in nodes if n.get("status") == "online"])
        logger.info(nodes)
    # nodes = configuration.get("NODES", [])  # Extract nodes to a list
    tasks = []
    # reuse previously opened client session by backend
    backend = api.backend
    logger.debug(type(backend))
    for node in nodes:
        logger.info(node)
        # Using a lambda or a helper function to ensure deferred evaluation
        new_api = ProxmoxAPI(backend=backend)
        tasks.append(
            new_api.nodes(node).status.get(
                filter_keys=["kversion", "cpuinfo", "memory.total", "uptime"]
            )
        )

    logger.info("Waiting for results... of resources: %s", len(tasks))
    results = await asyncio.gather(*tasks)
    # logger.info(len(results))
    for node, data in zip(nodes, results):
        # logger.debug(data)
        if data is not None:
            data = {
                "kversion": data.get("kversion", {}),
                "cpus": data.get("cpuinfo", {}).get("cpus", {}),
                "cpus_model": data.get("cpuinfo", {}).get("model", {}),
                "memory_total": human_readable_size(data.get("memory.total")),
                "uptime": str(timedelta(seconds=data.get("uptime", 0))),
            }
            # data = data.get("boot-info", {})
        else:
            data = None
        logger.info(f"Node: {node}, Result: {data}")


async def debug_get_node_status_parallel_safe(api: ProxmoxAPI):
    nodes: list[dict] = await api.nodes.get(filter_keys=["node", "status"])
    if nodes:
        nodes = sorted([n.get("node") for n in nodes if n.get("status") == "online"])
        logger.info(nodes)
    # nodes = configuration.get("NODES", [])  # Extract nodes to a list
    tasks = []
    # reuse previously opened client session by backend
    for node in nodes:
        logger.info(node)
        # Using a lambda or a helper function to ensure deferred evaluation
        tasks.append(
            api.nodes(node).status.get(
                filter_keys=["kversion", "cpuinfo", "memory.total", "uptime"]
            )
        )

    logger.info("Waiting for results... of resources: %s", len(tasks))
    results = await asyncio.gather(*tasks)
    # logger.info(len(results))
    for node, data in zip(nodes, results):
        # logger.debug(data)
        if data is not None:
            data = {
                "kversion": data.get("kversion", {}),
                "cpus": data.get("cpuinfo", {}).get("cpus", {}),
                "cpus_model": data.get("cpuinfo", {}).get("model", {}),
                "memory_total": human_readable_size(data.get("memory.total")),
                "uptime": str(timedelta(seconds=data.get("uptime", 0))),
            }
            # data = data.get("boot-info", {})
        else:
            data = None
        logger.info(f"Node: {node}, Result: {data}")


async def debug_low_level_get_node_status_parallel(api: ProxmoxAPI):
    nodes: list[dict] = await api.nodes.get(filter_keys=["node", "status"])
    if nodes:
        nodes = sorted([n.get("node") for n in nodes if n.get("status") == "online"])
        logger.info(nodes)
    tasks = []
    for node in nodes:
        logger.info(node)
        params = api.nodes(node).status.get(
            get_request_param=True,
        )
        tasks.append(
            api._async_execute(
                params=params,
                filter_keys=["kversion", "cpuinfo", "memory.total", "uptime"],
            )
        )

    logger.info("Waiting for results... of resources: %s", len(tasks))
    results = await asyncio.gather(*tasks)
    # logger.info(len(results))
    for node, data in zip(nodes, results):
        # logger.debug(data)
        if data is not None:
            data = {
                "kversion": data.get("kversion", {}),
                "cpus": data.get("cpuinfo", {}).get("cpus", {}),
                "cpus_model": data.get("cpuinfo", {}).get("model", {}),
                "memory_total": human_readable_size(data.get("memory.total")),
                "uptime": str(timedelta(seconds=data.get("uptime", 0))),
            }
            # data = data.get("boot-info", {})
        else:
            data = None
        logger.info(f"Node: {node}, Result: {data}")


async def debug_create_ha_group(api: ProxmoxAPI):
    logger.info("List live nodes:")
    nodes: list[dict] = await api.nodes.get(filter_keys=["node", "status"])
    if nodes:
        nodes_lst = sorted(
            [n.get("node") for n in nodes if n.get("status") == "online"]
        )
    else:
        nodes_lst = ["c01", "c02", "c03"]
    logger.info(nodes_lst)
    test_group_name = "test-gr-02-03f-04"
    test_group_nodes = ",".join(nodes_lst[:3])
    logger.info("List groups:")
    logger.info(await api.cluster.ha.groups.get(filter_keys="group"))
    logger.info(f"Create group: {test_group_name}, for nodes: {test_group_nodes}")
    logger.info(
        await api.cluster.ha.groups.create(
            data={"group": test_group_name, "nodes": test_group_nodes}
        )
    )
    logger.info(f"Get created group: {test_group_name}")
    logger.info(
        await api.cluster.ha.groups(test_group_name).get(filter_keys=["group", "nodes"])
    )
    logger.info(f"Delete group: {test_group_name}")
    logger.info(await api.cluster.ha.groups(test_group_name).delete())
    logger.info("List groups:")
    logger.info(await api.cluster.ha.groups.get(filter_keys="group"))


async def debug_low_level_get_version(api: ProxmoxAPI):
    # solution 1
    logger.info(params := api.version.get(get_request_param=True))
    logger.info(response := await api.async_request(**params))
    logger.info(api._response_analyze(response, filter_keys="version"))
    # solution 2
    logger.info(await api._async_execute(params=params, filter_keys="version"))

    logger.info(
        params := api.cluster.ha.groups.create(
            data={"group": "test_group_name", "nodes": "c01,c02"},
            get_request_param=True,
        )
    )
    logger.info(await api.async_request(**params))

    logger.info(
        params := api.cluster.ha.groups("test_group_name").get(get_request_param=True)
    )
    logger.info(await api.async_request(**params))

    logger.info(
        params := api.cluster.ha.groups("test_group_name").delete(
            get_request_param=True
        )
    )
    logger.info(await api.async_request(**params))


async def async_main():
    register_backends()
    async with ProxmoxAPI(backend_type="async") as api:
        try:
            # await debug_low_level_get_version(api)
            await debug_get_node_status_parallel_safe(api)
            # await debug_low_level_get_node_status_parallel(api)

            # params = api.version.create(
            #     data={"version": "1.1.1"}, get_request_param=True
            # )
            # logger.info(params)
            # logger.info(await api.version.get(filter_keys="version"))
            # logger.info("\n\nDebug_get_ha_groups\n")
            # await debug_get_ha_groups(api)
            # logger.info("\n\nDebug_create_ha_group\n")
            # await debug_create_ha_group(api)
            # logger.info("\n\nDebug_get_node_status_sequenced\n")
            # await debug_get_node_status_sequenced(api)
            # logger.info("\n\nDebug_get_node_status_parallel\n")
            # await debug_get_node_status_parallel(api)
        except Exception as e:
            logger.error(f"ERROR async_main: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(async_main())
    except Exception as e:
        logger.error(e)
