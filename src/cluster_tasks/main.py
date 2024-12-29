import logging

from cluster_tasks.ext_abs.base import AbstractHandler

logger = logging.getLogger("CT")


def cluster_tasks(handler: AbstractHandler):
    with handler as h:
        version = h.get_version()
    logger.info(f"API version: {version} {type(version)}")


async def acluster_tasks(handler: AbstractHandler):
    async with handler as h:
        version = await h.aget_version()
        logger.info(f"API version: {version} {type(version)}")
