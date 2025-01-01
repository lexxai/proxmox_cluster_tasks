import logging

import pytest

from cluster_tasks._api.handler import APIHandler


class CTLoggerFilter(logging.Filter):
    def filter(self, record):
        return record.name == "CT"  # Only allow logs from the "CT" logger


def pytest_configure(config):
    # Get the "CT" logger and set its level
    logger = logging.getLogger("CT")
    # logger.setLevel(logging.DEBUG)  # Adjust the level if needed
    logger.addFilter(CTLoggerFilter())  # Add the filter to the "CT" logger

    # Optionally, you can also add the filter to the root logger
    for handler in logging.root.handlers:
        handler.addFilter(CTLoggerFilter())  # Apply the filter globally


# @pytest.fixture(scope="session")
# def api_handler():
#     return APIHandler()


@pytest.fixture(scope="session")
def api_handler() -> APIHandler:
    with APIHandler() as handler:
        yield handler


# @pytest.fixture(scope="function")
# async def api_handler_async() -> APIHandler:
#     async with APIHandler() as handler:
#         yield handler


@pytest.fixture(scope="session")
def api_handler_async() -> APIHandler:
    return APIHandler()


# @pytest.fixture(scope="session")
# async def api_handler_async() -> APIHandler:
#     async with APIHandler() as handler:
#         yield handler
