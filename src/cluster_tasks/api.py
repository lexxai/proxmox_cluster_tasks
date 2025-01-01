import asyncio
import logging

from config.config import configuration
from cluster_tasks._api.handler import APIHandler
from cluster_tasks.main import acluster_tasks

logger = logging.getLogger("CT")


async def api():
    api_handler = APIHandler()
    await acluster_tasks(api_handler)


def main():
    # print(configuration.get("DEBUG"))
    logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
    logger.addHandler(logging.StreamHandler())
    logger.info("API Async Main")
    asyncio.run(api())


if __name__ == "__main__":
    main()
