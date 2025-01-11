import asyncio
import logging
import time

from cluster_tasks.tasks.base_tasks import BaseTasks

logger = logging.getLogger("CT.{__name__}")


class ProxmoxTasksBase(BaseTasks):
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

    def get_status_sync(self, upid: str, node: str = None) -> str | None:
        """
        Retrieve the status of a task synchronously by its UPID (Unique Process ID).

        Args:
            upid (str): The Unique Process ID of the task to check.
            node (str, optional): The name of the node where the task is running.
                If not provided, it is automatically determined by decoding the UPID.

        Returns:
            str | None: The status of the task as a string if available, or None if
            the UPID or node is invalid or the task status cannot be retrieved.

        Raises:
            Exception: Raised if an error occurs while fetching the task status.

        Notes:
            - The `decode_upid` method is used to extract the node from the UPID if
              the `node` argument is not explicitly provided.
            - Relies on the Proxmox API to retrieve task status.

        Example:
            status = instance.get_status_sync("UPID:pve1:0000ABCD")
            print(status)  # Outputs the task status or None
        """
        if not node:
            node = self.decode_upid(upid).get("node")
        if upid and node:
            result = self.api.nodes(node).tasks(upid).status.get(filter_keys="status")
            return result

    async def get_status_async(self, upid: str, node: str = None) -> str | None:
        """
        Retrieve the status of a task asynchronously by its UPID (Unique Process ID).

        Args:
            upid (str): The Unique Process ID of the task to check.
            node (str, optional): The name of the node where the task is running.
                If not provided, it is automatically determined by decoding the UPID.

        Returns:
            str | None: The status of the task as a string if available, or None if
            the UPID or node is invalid or the task status cannot be retrieved.

        Raises:
            Exception: Raised if an error occurs while fetching the task status.

        Notes:
            - The `decode_upid` method is used to extract the node from the UPID if
              the `node` argument is not explicitly provided.
            - Relies on the Proxmox API to retrieve task status.

        Example:
            status = instance.get_status_sync("UPID:pve1:0000ABCD")
            print(status)  # Outputs the task status or None
        """
        if not node:
            node = self.decode_upid(upid).get("node")
        if upid and node:
            result = (
                await self.api.nodes(node).tasks(upid).status.get(filter_keys="status")
            )
            return result

    def wait_task_done_sync(self, upid: str, node: str = None) -> bool:
        """
        Synchronously waits for a task to complete.
        """
        start_time = time.time()
        while (result := self.get_status_sync(upid, node)) is not None:
            if result == "stopped":
                return True
            duration = time.time() - start_time
            formatted_duration = self.format_duration(duration)
            formatted_timeout = self.format_duration(self.timeout)
            formated_upid = self.shorten_upid(upid, 1, 7)
            logger.info(
                f"Waiting for task ({formated_upid}) to finish... [ {formatted_duration} / {formatted_timeout} ]"
            )
            time.sleep(self.polling_interval)
            if time.time() - start_time > self.timeout:
                logger.warning(
                    f"Timeout reached while waiting for task to finish. {self.shorten_upid(upid)}..."
                )
                break
        return False

    async def wait_task_done_async(self, upid: str, node: str = None) -> bool:
        """
        Asynchronously waits for a task to complete.
        """
        start_time = time.time()
        while (result := await self.get_status_async(upid, node)) is not None:
            if result == "stopped":
                return True
            duration = time.time() - start_time
            formatted_duration = self.format_duration(duration)
            formatted_timeout = self.format_duration(self.timeout)
            formated_upid = self.shorten_upid(upid, 1, 7)
            logger.info(
                f"Waiting for task ({formated_upid}) to finish... [ {formatted_duration} / {formatted_timeout} ]"
            )
            await asyncio.sleep(self.polling_interval)
            if time.time() - start_time > self.timeout:
                logger.warning(
                    f"Timeout reached while waiting for task to finish. {self.shorten_upid(upid)}..."
                )
                break
        return False

    @staticmethod
    def decode_upid(upid: str) -> dict:
        """
        Decodes the sections of a UPID into separate fields
        https://github.com/proxmoxer/proxmoxer/blob/develop/proxmoxer/tools/tasks.py

        :param upid: a UPID string
        :type upid: str
        :return: The decoded information from the UPID
        :rtype: dict
        """
        segments = upid.split(":")
        if segments[0] != "UPID" or len(segments) != 9:
            raise ValueError("UPID is not in the correct format")

        data = {
            "upid": upid,
            "node": segments[1],
            "pid": int(segments[2], 16),
            "pstart": int(segments[3], 16),
            "starttime": int(segments[4], 16),
            "type": segments[5],
            "id": segments[6],
            "user": segments[7].split("!")[0],
            "comment": segments[8],
        }
        return data

    @staticmethod
    def shorten_upid(upid: str, start: int = 0, length: int = 7) -> str | None:
        if upid:
            return ":".join(upid.split(":")[start:length])
