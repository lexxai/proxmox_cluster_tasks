import logging

from cluster_tasks.ext_abs.base import AbstractHandler

logger = logging.getLogger("CT")


def cluster_tasks(handler: AbstractHandler):
    with handler as h:
        try:
            version = h.get_version()
            logger.info(f"API version: {version} {type(version)}")
        except Exception as e:
            logger.error(f"ERROR cluster_tasks: {e}")


async def acluster_tasks(handler: AbstractHandler):
    async with handler as h:
        try:
            version = await h.aget_version()
            logger.info(f"API version: {version} {type(version)}")
        except Exception as e:
            logger.error(f"ERROR acluster_tasks: {e}")
