from datetime import timedelta
from ext_api.proxmox_api import ProxmoxAPI


class BaseTasks:
    """
    BaseTasks class that provides common functionality for tasks interacting
    with the Proxmox API. It manages timeouts, loop sleeps, and provides utility
    methods for formatting durations.

    Attributes:
        timeout (int): The default timeout in seconds for tasks.
        loop_sleep (int): The default sleep duration between task loops in seconds.
        _api (ProxmoxAPI): The Proxmox API instance used for interacting with Proxmox.
    """

    timeout = 10 * 60  # 10 minutes
    polling_interval = 2

    def __init__(
        self,
        api: ProxmoxAPI,
        timeout: int = timeout,
        polling_interval: int = polling_interval,
    ):
        """
        Initializes the BaseTasks class with the given Proxmox API instance and optional
        timeout and loop sleep values.

        Args:
            api (ProxmoxAPI): The Proxmox API instance for making API calls.
            timeout (int, optional): The timeout value for tasks (default is 60).
            polling_interval (int, optional): The sleep time between loops in seconds (default is 2).
        """
        self._api: ProxmoxAPI = api
        self.timeout = timeout
        self.polling_interval = polling_interval

    @property
    def api(self):
        """
        Gets the Proxmox API instance.

        Returns:
            ProxmoxAPI: The Proxmox API instance.
        """
        return self._api

    @api.setter
    def api(self, value):
        """
        Sets a new Proxmox API instance.

        Args:
            value (ProxmoxAPI): The new Proxmox API instance to set.
        """
        self._api = value

    @staticmethod
    def format_duration(seconds: float | int) -> str:
        """
        Formats a duration (in seconds) as a string in the format HH:MM:SS.

        Args:
            seconds (float or int): The duration in seconds to format.

        Returns:
            str: The formatted duration as HH:MM:SS.
        """
        return str(timedelta(seconds=seconds)).split(".")[0]
