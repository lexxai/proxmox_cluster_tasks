import logging

import httpx

from cluster_tasks.backends.abstract_backends import (
    AbstractBackend,
    AbstractAsyncBackend,
)
from cluster_tasks.config import configuration

# from cluster_tasks.ext_abs.backends import Backend, AsyncBackend

logger = logging.getLogger(f"CT.{__name__}")


class BackendAbstractHTTP:
    def __init__(
        self, base_url=None, token_id=None, token_secret=None, verify_ssl=None
    ):
        super().__init__()
        self.entry_points: dict = configuration.get("API_HANDLERS")
        self.api_node_url = base_url or configuration.get("API.NODE_URL")
        self.token_id = token_id or configuration.get("API.TOKEN_ID")
        self.token_secret = token_secret or configuration.get("API.TOKEN_SECRET")
        self.api_verify_ssl = (
            verify_ssl
            if verify_ssl is not None
            else configuration.get("API.VERIFY_SSL", True)
        )
        self.client = None

    @staticmethod
    def get_authorization() -> str | None:
        token_id = configuration.get("API.TOKEN_ID")
        token_secret = configuration.get("API.TOKEN_SECRET")
        if not all([token_id, token_secret]):
            logger.error("API token not found")
            return None
        authorization = f"PVEAPIToken={token_id}={token_secret}"
        return authorization

    def get_headers(self, headers):
        _headers = {
            "Authorization": self.get_authorization(),
            "content-type": "application/json",
        }
        if headers:
            _headers.update(headers)
        return _headers

    def process_data(self, input_data: dict | None = None) -> dict:
        if not input_data:
            return {"message": "Input data is required"}
        if "entry_point" not in input_data:
            return {"message": "Entry point is missing"}
        method = input_data.get("method", "GET").upper()
        entry_point = input_data.get("entry_point")
        data = input_data.get("data")
        params = input_data.get("params")
        url = "".join([self.api_node_url, entry_point])
        logger.debug(f"{method=} {entry_point=} {data=} {params=}")
        return {"method": method, "url": url, "data": data, "params": params}


class BackendHTTP(BackendAbstractHTTP, AbstractBackend):

    def __enter__(self):
        # print("API Enter")
        self.client = self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # print("API Exit")
        self.close()
        return True

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    def connect(self, *args, **kwargs):
        headers = kwargs.get("headers", None)
        verify_ssl = self.api_verify_ssl
        client = httpx.Client(
            http2=True, headers=self.get_headers(headers), verify=verify_ssl
        )
        return client

    def process(self, input_data: dict | None = None) -> dict:
        result = {}
        if self.client is None:
            self.client = self.connect()
        process_data = self.process_data(input_data)
        if process_data and "message" in process_data:
            result.update({"message": process_data.get("message")})
            return result
        response = self.client.request(**process_data)
        if response.status_code < 400:
            result.update(response.json())
        return {"result": result, "status_code": response.status_code}


class BackendAsyncHTTP(BackendAbstractHTTP, AbstractAsyncBackend):

    async def __aenter__(self):
        logger.debug("API Async Enter")
        self.client = await self.aconnect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        logger.debug("API Async Exit")
        await self.aclose()
        return True

    async def aclose(self):
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    async def aconnect(self, *args, **kwargs):
        headers = kwargs.get("headers", None)
        verify_ssl = self.api_verify_ssl
        client = httpx.AsyncClient(
            http2=True, headers=self.get_headers(headers), verify=verify_ssl
        )
        return client

    async def aprocess(self, input_data: dict | None = None) -> dict:
        result = {}
        if self.client is None:
            self.client = await self.aconnect()
        process_data = self.process_data(input_data)
        if process_data and "message" in process_data:
            result.update({"message": process_data.get("message")})
            return result
        response = await self.client.request(**process_data)
        if response.status_code < 400:
            result.update(response.json())
        return {"result": result, "status_code": response.status_code}
