import logging

import pytest

from cluster_tasks.config import configuration

# logger = logging.getLogger("CT")
# logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
# logger.info(configuration.get("NODES"))


#
def test_api_version(api_handler):
    # with api_handler as handler:
    version = api_handler.get_version()
    # print(version)
    assert version["status_code"] == 200
    assert version["result"]["data"]["version"]


def test_api_version2(api_handler):
    # with api_handler as handler:
    version = api_handler.get_version()
    # print(version)
    assert version["status_code"] == 200
    assert version["result"]["data"]["version"]


#
@pytest.mark.asyncio
async def test_api_version_async(api_handler_async):
    async with api_handler_async as handler:
        version = await handler.aget_version()
    # print(version)
    assert version["status_code"] == 200
    assert version["result"]["data"]["version"]


@pytest.mark.asyncio
async def test_api_version_async2(api_handler_async):
    async with api_handler_async as handler:
        version = await handler.aget_version()
    # print(version)
    assert version["status_code"] == 200
    assert version["result"]["data"]["version"]


# @pytest.mark.asyncio
# async def test_api_version_async(api_handler_async):
#     version = await api_handler_async.aget_version()
#     print(version)
#     assert version["status_code"] == 200
#     assert version["result"]["data"]["version"]
