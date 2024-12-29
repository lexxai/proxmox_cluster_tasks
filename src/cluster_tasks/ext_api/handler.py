import logging
from pyexpat.errors import messages

import httpx

from cluster_tasks.ext_abs.base import AbstractHandler
from cluster_tasks.config import configuration


logger = logging.getLogger("CT.{__name__}")


class APIHandler(AbstractHandler):
    """Concrete implementation for handling API logic."""

    def __init__(self):
        super().__init__()
        self.entry_points: dict = configuration.get("API_HANDLERS")
        self.api_node_url: str = configuration.get("API.NODE_URL")
        self.client = None

    def __enter__(self):
        self.client = self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()
        self.client = None
        return True

    def connect(self, headers=None):
        _headers = {
            "Authorization": self.get_authorization(),
            "content-type": "application/json",
        }
        if headers:
            _headers.update(headers)
        # print(_headers)
        client = httpx.Client(http2=True, headers=_headers)
        return client

    @staticmethod
    def get_authorization():
        token_id = configuration.get("API.TOKEN_ID")
        token_secret = configuration.get("API.TOKEN_SECRET")
        authorization = f"PVEAPIToken={token_id}={token_secret}"
        return authorization

    def process(self, input_data: dict | None = None) -> dict:
        # print(f"Processing API data: {input_data}")
        method = input_data.get("method", "GET").upper()
        entry_point = input_data.get("entry_point")
        data = input_data.get("data")
        if entry_point is None:
            return {
                "result": None,
                "message": "API endpoint not found",
                "status_code": None,
            }
        entry_point_fmt = entry_point.format(TARGETNODE=input_data.get("TARGETNODE"))
        url = "".join([self.api_node_url, entry_point_fmt])
        result = None
        response = self.client.request(method=method, url=url, data=data)
        if response.status_code < 400:
            result = response.json()
        # API-specific logic here
        return {"result": result, "status_code": response.status_code}

    def get_version(self):
        input_data = {
            "entry_point": self.entry_points.get("VERSION"),
            "method": "GET",
        }
        return self.process(input_data)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    with APIHandler() as api_handler:
        print(api_handler.get_version())
