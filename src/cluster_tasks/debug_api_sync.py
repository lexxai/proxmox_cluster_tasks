import concurrent
import logging
import queue
from concurrent.futures import ThreadPoolExecutor

from cluster_tasks.configure_logging import config_logger
from config.config import configuration
from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI

# Example usage
logger = logging.getLogger("CT")
logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
config_logger(logger)

MAX_THREADS = 4

register_backends("https")
clients = [ProxmoxAPI(backend_name="https") for _ in range(MAX_THREADS)]
client_queue = queue.Queue()

# Populate the queue with clients
for c in clients:
    client_queue.put(c)


def get_version():
    client = client_queue.get()
    try:
        # Get an available client from the queue
        with client as api:
            response1 = api.version.get()
            response2 = api.version.get()
        return [response1, response2]
    finally:
        # Return the client to the queue
        client_queue.put(client)


def demo_thread_pool_get_version():
    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for _ in range(20):
            logger.debug(f"Task submit: {len(tasks)}")
            tasks.append(executor.submit(get_version))
    logger.debug("futures created")
    # time.sleep(2)
    # for task in tasks:
    for task in concurrent.futures.as_completed(tasks):
        logger.info(task.result())


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
    demo_thread_pool_get_version()
    demo_sequenced_session()


if __name__ == "__main__":
    main()
