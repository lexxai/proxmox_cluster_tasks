from datetime import timedelta

from ext_api.proxmox_api import ProxmoxAPI


class BaseTasks:
    TIMEOUT = 60
    LOOP_SLEEP = 2

    def __init__(self, api: ProxmoxAPI):
        self._api: ProxmoxAPI = api

    @property
    def api(self):
        return self._api

    @api.setter
    def api(self, value):
        self._api = value

    @staticmethod
    def format_duration(seconds: float | int) -> str:
        """Format a duration (in seconds) as HH:MM:SS."""
        return str(timedelta(seconds=seconds)).split(".")[0]
