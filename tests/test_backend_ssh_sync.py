import copy
import unittest

from unittest import mock

from config.config import ConfigLoader
from ext_api.backends.backend_registry import BackendRegistry
from ext_api.backends.registry import register_backends
from tests.conftest import export_mock_backend_settings


class BackendRequestSSHTest(unittest.TestCase):

    mock_backend_settings = None  # Explicitly declare the attribute

    common_request_data = {
        "version.get": {
            "request_params": {
                "method": "get",
                "endpoint": "version",
            },
            "return_value": '{"release":"8.3","repoid":"3e76eec21c4a14a7","version":"8.3.2"}',
        }
    }

    def setUp(self):
        self.mock_backend_settings = export_mock_backend_settings()
        backend_name = "ssh"
        register_backends(backend_name)
        backend_cls = BackendRegistry.get_backend(backend_name)
        if self.mock_backend_settings.get(backend_name.upper()):
            backend = backend_cls(
                entry_point="echo", hostname="localhost", username="fake_user"
            )
        else:
            # Use Real Configuration
            configuration = ConfigLoader()
            backend = backend_cls(
                entry_point=configuration.get("CLI.ENTRY_POINT"),
                hostname=configuration.get("SSH.HOSTNAME"),
                username=configuration.get("SSH.USERNAME"),
            )

        if self.mock_backend_settings.get(backend_name.upper()) and hasattr(
            backend, "connect"
        ):
            mock_connect = mock.MagicMock()
            backend._client = mock.MagicMock()
            mock.patch.object(backend, "connect", side_effect=mock_connect)

        self.backend = backend
        self.backend_name = backend_name

    def _request_backend_sync(
        self,
        request_params=None,
        return_value=None,
        return_code: int = 0,
        is_error: bool = False,
    ):
        patcher = None
        if self.mock_backend_settings.get(self.backend_name.upper(), True):
            mock_stdout = mock.MagicMock()
            mock_stdout.read.return_value = (
                return_value.encode() if return_value else b""
            )
            mock_stdout.channel.recv_exit_status.return_value = return_code

            mock_stderr = mock.MagicMock()
            mock_stderr.read.return_value = b""  # Simulating empty stderr

            def mock_exec(command, *args, **kwargs):
                # print("mock_exec", command)
                if is_error:
                    raise Exception(  # Simulate an SSH error
                        "run mocked Command '{}' failed with return code {}: {}".format(
                            command, 1, "mock error output"
                        )
                    )
                return (None, mock_stdout, mock_stderr)

            patcher = mock.patch.object(
                self.backend.client, "exec_command", side_effect=mock_exec
            )
            patcher.start()

        try:
            result = self.backend.request(**request_params)
        finally:
            if patcher:
                patcher.stop()
        return result

    def test_request_success_backend_sync(self):
        request_data = self.common_request_data.get("version.get")
        result = self._request_backend_sync(
            request_params=request_data.get("request_params"),
            return_value=request_data.get("return_value"),
        )
        self.assertIsNotNone(result)
        response = result.get("response")
        self.assertIsNotNone(response)
        data = response.get("data")
        self.assertIsNotNone(data)
        self.assertIsNotNone(data.get("release"))
        self.assertEqual(result["status_code"], 0)
        self.assertTrue(result["success"])

    def test_request_failure_backend_sync(self):
        request_data = self.common_request_data.get("version.get")
        result = self._request_backend_sync(
            request_params=request_data.get("request_params"),
            return_value=request_data.get("return_value"),
            is_error=True,
        )
        self.assertIsNotNone(result["response"])
        self.assertNotEqual(result["status_code"], 0)
        self.assertFalse(result["success"])

    def test_request_no_command_backend_sync(self):
        # Test behavior when format_command returns None

        request_data = copy.deepcopy(self.common_request_data.get("version.get"))
        request_data["request_params"]["endpoint"] = ""
        result = self._request_backend_sync(
            request_params=request_data.get("request_params"),
        )
        self.assertIsNotNone(result["response"])
        self.assertNotEqual(result["status_code"], 0)
        self.assertFalse(result["success"])


if __name__ == "__main__":
    unittest.main()
