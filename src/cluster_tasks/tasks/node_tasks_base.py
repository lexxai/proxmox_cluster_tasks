import asyncio
import logging
import time

from cluster_tasks.tasks.base_tasks import BaseTasks

logger = logging.getLogger("CT.{__name__}")


class NodeTasksBase(BaseTasks):
    """
    Base class with shared logic for both sync and async task handling.
    Contains methods for both sync and async API calls.
    Methods:
        get_status_sync(node: str, upid: str) -> str | None:
            Retrieves the status of a task by its UPID.

        wait_task_done_sync(node: str, upid: str) -> bool:
            Waits for a task to complete, checking the status periodically.

        get_status_async(node: str, upid: str) -> str | None:
            Retrieves the status of a task by its UPID.

        wait_task_done_async(node: str, upid: str) -> bool:
            Waits for a task to complete, checking the status periodically.
    """

    def get_status_sync(self, node: str, upid: str) -> str | None:
        """
        Synchronously retrieves the status of a task identified by its UPID.
        """
        if upid:
            result = self.api.nodes(node).tasks(upid).status.get(filter_keys="status")
            return result

    async def get_status_async(self, node: str, upid: str) -> str | None:
        """
        Asynchronously retrieves the status of a task identified by its UPID.
        """
        if upid:
            result = (
                await self.api.nodes(node).tasks(upid).status.get(filter_keys="status")
            )
            return result

    def wait_task_done_sync(self, node: str, upid: str) -> bool:
        """
        Synchronously waits for a task to complete.
        """
        start_time = time.time()
        while (result := self.get_status_sync(node, upid)) is not None:
            if result == "stopped":
                return True
            duration = time.time() - start_time
            formatted_duration = self.format_duration(duration)
            formatted_timeout = self.format_duration(self.timeout)
            logger.info(
                f"Waiting for task to finish... [ {formatted_duration} / {formatted_timeout} ]"
            )
            time.sleep(self.loop_sleep)
            if time.time() - start_time > self.timeout:
                logger.warning(
                    f"Timeout reached while waiting for task to finish. {upid=}"
                )
                break
        return False

    async def wait_task_done_async(self, node: str, upid: str) -> bool:
        """
        Asynchronously waits for a task to complete.
        """
        start_time = time.time()
        while (result := await self.get_status_async(node, upid)) is not None:
            if result == "stopped":
                return True
            duration = time.time() - start_time
            formatted_duration = self.format_duration(duration)
            formatted_timeout = self.format_duration(self.timeout)
            logger.info(
                f"Waiting for task to finish... [ {formatted_duration} / {formatted_timeout} ]"
            )
            await asyncio.sleep(self.loop_sleep)
            if time.time() - start_time > self.timeout:
                logger.warning(
                    f"Timeout reached while waiting for task to finish. {upid=}"
                )
                break
        return False
