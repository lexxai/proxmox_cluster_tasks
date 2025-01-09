import logging
import os

import pytest

# import sys
# from pathlib import Path
# project_root = Path(__file__).resolve().parent.parent
# src_path = project_root / "src"
# sys.path.insert(0, str(src_path))


from ext_api.backends.registry import register_backends
from ext_api.proxmox_api import ProxmoxAPI


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

    register_backends()


@pytest.fixture(scope="session")
def mock_backend_settings():
    return {
        "HTTPS": os.getenv("MOCK_BACKEND_HTTPS", "true").lower() == "true",
        "SSH": os.getenv("MOCK_BACKEND_SSH", "true").lower() == "true",
        "CLI": os.getenv("MOCK_BACKEND_CLI", "true").lower() == "true",
    }


@pytest.fixture(scope="session")
def get_api(request) -> ProxmoxAPI:
    backend_name = (
        request.param.get("backend_name", "https")
        if hasattr(request, "param")
        else "https"
    )
    with ProxmoxAPI(backend_name=backend_name, backend_type="sync") as api:
        yield api


@pytest.fixture(scope="session")
def get_api_async(request) -> ProxmoxAPI:
    backend_name = (
        request.param.get("backend_name", "https")
        if hasattr(request, "param")
        else "https"
    )
    return ProxmoxAPI(backend_name=backend_name, backend_type="async")
