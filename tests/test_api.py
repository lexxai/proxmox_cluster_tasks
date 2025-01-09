import subprocess

import httpx
import pytest


# logger = logging.getLogger("CT")
# logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
# logger.info(configuration.get("NODES"))


#
@pytest.mark.parametrize("get_api", [{"backend_name": "https"}], indirect=True)
def test_api_version_https(mock_backend_settings, get_api, mocker):
    if mock_backend_settings.get("HTTPS"):
        http_result = '{"data":{"repoid":"3e76eec21c4a14a7","release":"mock-8.3","version":"8.3.2"}}'

        def mock_request(method, url, **kwargs):
            return httpx.Response(status_code=200, text=http_result)

        mocker.patch.object(get_api.backend.client, "request", side_effect=mock_request)
    version = get_api.version.get()
    assert version
    assert version.get("release")
    assert version.get("release") == "mock-8.3"


@pytest.mark.parametrize("get_api", [{"backend_name": "ssh"}], indirect=True)
def test_api_version_ssh(mock_backend_settings, get_api, mocker):
    if mock_backend_settings.get("SSH"):
        ssh_result = '{"release":"8.3","repoid":"3e76eec21c4a14a7","version":"8.3.2"}'

        mock_stdout = mocker.MagicMock()
        mock_stdout.read.return_value = ssh_result.encode()
        mock_stdout.channel.recv_exit_status.return_value = 0

        mock_stderr = mocker.MagicMock()
        mock_stderr.read.return_value = b""  # Simulating empty stderr

        def mock_exec(command, *args, **kwargs):
            return (None, mock_stdout, mock_stderr)

        mocker.patch.object(
            get_api.backend.client, "exec_command", side_effect=mock_exec
        )
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
async def test_api_version_https_async(mock_backend_settings, get_api_async, mocker):
    async with get_api_async as api:
        if mock_backend_settings.get("HTTPS"):
            http_result = '{"data":{"repoid":"3e76eec21c4a14a7","release":"mock-8.3","version":"8.3.2"}}'

            async def mock_request(method, url, **kwargs):
                return httpx.Response(status_code=200, text=http_result)

            mocker.patch.object(api.backend.client, "request", side_effect=mock_request)
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
