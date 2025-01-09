import subprocess

import pytest


# logger = logging.getLogger("CT")
# logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
# logger.info(configuration.get("NODES"))


#
@pytest.mark.parametrize("get_api", [{"backend_name": "https"}], indirect=True)
def test_api_version_https(get_api):
    version = get_api.version.get()
    assert version
    assert version.get("release")


@pytest.mark.parametrize("get_api", [{"backend_name": "ssh"}], indirect=True)
def test_api_version_ssh(get_api):
    version = get_api.version.get()
    assert version
    assert version.get("release")


@pytest.mark.parametrize("get_api", [{"backend_name": "cli"}], indirect=True)
def test_api_version_cli(mock_backend_settings, get_api, mocker):
    if mock_backend_settings.get("CLI"):
        subprocess_result = (
            '{"release":"8.3","repoid":"3e76eec21c4a14a7","version":"8.3.2"}'
        )
        mock_subprocess = mocker.patch("subprocess.run")
        mock_subprocess.return_value = subprocess.CompletedProcess(
            args=["command"], returncode=0, stdout=subprocess_result
        )
    version = get_api.version.get()
    assert version
    assert version.get("version") == "8.3.2"


@pytest.mark.asyncio
@pytest.mark.parametrize("get_api_async", [{"backend_name": "https"}], indirect=True)
async def test_api_version_https_async(get_api_async):
    async with get_api_async as api:
        version = await api.version.get()
    assert version
    assert version.get("release")


@pytest.mark.asyncio
@pytest.mark.parametrize("get_api_async", [{"backend_name": "ssh"}], indirect=True)
async def test_api_version_ssh_async(get_api_async):
    async with get_api_async as api:
        version = await api.version.get()
    assert version
    assert version.get("release")


@pytest.mark.asyncio
@pytest.mark.parametrize("get_api_async", [{"backend_name": "cli"}], indirect=True)
async def test_api_version_cli_async(mock_backend_settings, get_api_async, mocker):
    if mock_backend_settings.get("CLI"):
        subprocess_result = (
            '{"release":"8.3","repoid":"3e76eec21c4a14a7","version":"8.3.2"}'
        )
        mock_process = mocker.MagicMock()
        mock_process.communicate = mocker.AsyncMock(
            return_value=(subprocess_result.encode(), b"")
        )
        mock_process.returncode = 0
        mocker.patch("asyncio.create_subprocess_shell", return_value=mock_process)

    async with get_api_async as api:
        version = await api.version.get()
    assert version
    assert version.get("version") == "8.3.2"


# @pytest.mark.asyncio
# async def test_api_version_async2(api_handler_async):
#     async with api_handler_async as handler:
#         version = await handler.aget_version()
#     # print(version)
#     assert version["status_code"] == 200
#     assert version["result"]["data"]["version"]


# @pytest.mark.asyncio
# async def test_api_version_async(api_handler_async):
#     version = await api_handler_async.aget_version()
#     print(version)
#     assert version["status_code"] == 200
#     assert version["result"]["data"]["version"]
