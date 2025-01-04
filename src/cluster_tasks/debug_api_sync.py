import concurrent
import logging
import queue
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from cluster_tasks.configure_logging import config_logger
from config.config import configuration
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI

# Example usage
logger = logging.getLogger("CT")
logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
config_logger(logger)

MAX_THREADS = 4

register_backends()
clients = [ProxmoxAPI(backend_name="https") for _ in range(MAX_THREADS)]
client_queue = queue.Queue()

# Populate the queue with clients
for c in clients:
    client_queue.put(c)


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


def get_version():
    client = client_queue.get()
    try:
        # Get an available client from the queue
        with client as api:
            response = api.version.get(filter_keys="version")
        return response
    finally:
        # Return the client to the queue
        client_queue.put(client)


def get_node_status(node):
    client = client_queue.get()
    try:
        # Get an available client from the queue
        with client as api:
            response = api.nodes(node).status.get(
                filter_keys=["kversion", "cpuinfo", "memory.total", "uptime"]
            )
        return response
    finally:
        # Return the client to the queue
        client_queue.put(client)


def debug_thread_pool_get_node_status_parallel():
    client = client_queue.get()
    try:
        with client as api:
            nodes: list[dict] = api.nodes.get(filter_keys=["node", "status"])
    finally:
        client_queue.put(client)

    if nodes:
        nodes = sorted([n.get("node") for n in nodes if n.get("status") == "online"])
    logger.info(nodes)

    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for node in nodes:
            logger.debug(f"Task submit: {len(tasks)}")
            tasks.append(executor.submit(get_node_status, node))
    logger.debug("futures created")

    logger.info("Waiting for results... of resources: %s", len(tasks))
    # logger.info(len(results))
    for node, data in zip(nodes, [task.result() for task in tasks]):
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


def demo_thread_pool_get_version():
    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for _ in range(8):
            logger.debug(f"Task submit: {len(tasks)}")
            tasks.append(executor.submit(get_version))
    logger.info("futures created")
    results = [task.result() for task in tasks]
    logger.info(results)


def demo_sequenced_session():
    API = ProxmoxAPI(backend_name="https")
    with API as api:
        # Simulate API calls
        logger.info(api.version.get())

        # logger.info(sorted([n.get("id") for n in api.nodes.get()]))
        # logger.info(api.nodes.get(filter_keys=["node", "status"]))
        # logger.info(api.nodes.get())
        # logger.info(api.nodes("c01").status.get())
        # logger.info(api.cluster.ha.groups.create(name="test-gr02", nodes="c01,c02:100"))

        # print(response2)


def main():
    # debug_thread_pool_get_node_status_parallel()
    demo_thread_pool_get_version()
    # demo_sequenced_session()


if __name__ == "__main__":
    main()
