import logging

import httpx

from cluster_tasks.ext_abs.base import AbstractHandler
from cluster_tasks.config import configuration


logger = logging.getLogger(f"CT.{__name__}")


class APIHandler(AbstractHandler):
    """Concrete implementation for handling API logic."""

    def __init__(self):
        super().__init__()
        self.entry_points: dict = configuration.get("API_HANDLERS")
        self.api_node_url: str = configuration.get("API.NODE_URL")
        self.client = None

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    async def aclose(self):
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    def __enter__(self):
        # print("API Enter")
        self.client = self.connect()
        return self

    async def __aenter__(self):
        logger.debug("API Async Enter")
        self.client = await self.aconnect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # print("API Exit")
        self.close()
        return True

    async def __aexit__(self, exc_type, exc_value, traceback):
        logger.debug("API Async Exit")
        await self.aclose()
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

    async def aconnect(self, headers=None):
        _headers = {
            "Authorization": self.get_authorization(),
            "content-type": "application/json",
        }
        if headers:
            _headers.update(headers)
        # print(_headers)
        client = httpx.AsyncClient(http2=True, headers=_headers)
        return client

    @staticmethod
    def get_authorization() -> str | None:
        token_id = configuration.get("API.TOKEN_ID")
        token_secret = configuration.get("API.TOKEN_SECRET")
        if not all([token_id, token_secret]):
            logger.error("API token not found")
            return None
        authorization = f"PVEAPIToken={token_id}={token_secret}"
        return authorization

    def process_data(self, input_data: dict | None = None) -> dict:
        method = input_data.get("method", "GET").upper()
        entry_point = input_data.get("entry_point")
        if entry_point is None:
            return {"message": "API endpoint not found"}
        data = input_data.get("data")
        params = input_data.get("params")
        entry_point_fmt = entry_point.format(TARGETNODE=input_data.get("TARGETNODE"))
        url = "".join([self.api_node_url, entry_point_fmt])
        logger.debug(f"{method=} {url=} {data=} {params=}")
        return {"method": method, "url": url, "data": data, "params": params}

    def process(self, input_data: dict | None = None) -> dict:
        result = {
            "result": None,
            "status_code": None,
        }
        if self.client is None:
            self.client = self.connect()
        process_data = self.process_data(input_data)
        if process_data and "message" in process_data:
            result.update({"message": process_data.get("message")})
            return result
        response = self.client.request(**process_data)
        if response.status_code < 400:
            result = response.json()
        return {"result": result, "status_code": response.status_code}

    async def aprocess(self, input_data: dict | None = None) -> dict:
        result = {
            "result": None,
            "status_code": None,
        }
        if self.client is None:
            self.client = await self.aconnect()
        process_data = self.process_data(input_data)
        if process_data and "message" in process_data:
            result.update({"message": process_data.get("message")})
            return result
        response = await self.client.request(**process_data)
        if response.status_code < 400:
            result = response.json()
        return {"result": result, "status_code": response.status_code}

    # GET VERSION
    def get_version_data(self) -> dict:
        input_data = {
            "entry_point": self.entry_points.get("VERSION"),
            "method": "GET",
        }
        return input_data

    def get_version(self):
        return self.process(self.get_version_data())

    async def aget_version(self):
        return await self.aprocess(self.get_version_data())

    # HA_GROUPS
    # GET HA_GROUPS
    def get_ha_groups_data(self) -> dict:
        input_data = {
            "entry_point": self.entry_points.get("HA_GROUPS"),
            "method": "GET",
        }
        return input_data

    def get_ha_groups(self):
        return self.process(self.get_ha_groups_data())

    async def aget_ha_groups(self):
        return await self.aprocess(self.get_ha_groups_data())


if __name__ == "__main__":
    logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
    logger.addHandler(logging.StreamHandler())
    logger.info(configuration.get("NODES"))
    # with APIHandler() as api_handler:
    #     logger.info(api_handler.get_version())

    import asyncio

    async def amain():
        async with APIHandler() as api_handler:
            logger.info(await api_handler.aget_version())
            logger.info(await api_handler.aget_ha_groups())

    asyncio.run(amain())
