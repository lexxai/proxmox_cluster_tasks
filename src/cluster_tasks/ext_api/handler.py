import httpx
from cluster_tasks.ext_abs.base import AbstractHandler

from cluster_tasks.config import configuration


class APIHandler(AbstractHandler):
    """Concrete implementation for handling API logic."""

    def __init__(self):
        super().__init__()
        self.entry_points = configuration.get("api_handlers")
        self.api_url = configuration.get("api_url")
        self.client = None

    def connect(self, headers=None):
        _headers = {
            "Authorization": f"Bearer {configuration.get('api_token')}",
            "content-type": "application/json",
        }
        if headers:
            _headers.update(headers)
        client = httpx.Client(http2=True, headers=_headers)
        return client

    def process(self, input_data: dict | None = None):
        print(f"Processing API data: {input_data}")
        method = input_data.get("method", "GET")
        entry_point = input_data.get("entry_point")
        if entry_point is None:
            return {"result": "API endpoint not found"}
        url = "/".join([self.api_url, entry_point])
        # API-specific logic here
        return {"result": f"API processed {input_data}"}

    def get_version(self):
        input_data = {
            "entry_point": self.entry_points.get("version"),
            "method": "GET",
        }

        return self.process(input_data)
