import unittest

from unittest import mock
import subprocess

from ext_api.backends.backend_registry import BackendRegistry
from ext_api.backends.registry import register_backends
from tests.conftest import export_mock_backend_settings


class BackendRequestCLITest(unittest.TestCase):

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
        backend_name = "cli"
        register_backends(backend_name)
        backend_cls = BackendRegistry.get_backend(backend_name)
        backend = backend_cls(entry_point="pvesh")
        if self.mock_backend_settings.get(backend_name.upper()) and hasattr(
            backend, "connect"
        ):
            mock_connect = mock.MagicMock()
            backend._client = mock.MagicMock()
            mock.patch.object(backend, "connect", side_effect=mock_connect)

        self.backend = backend

    def _request_backend_sync(
        self,
        request_params=None,
        return_value=None,
        return_code: int = 0,
        is_error: bool = False,
        mock_subprocess_run=None,
    ):
        if (
            self.mock_backend_settings.get("CLI", True)
            and mock_subprocess_run is not None
        ):
            # Mock a successful subprocess run
            mock_process = mock.MagicMock()
            mock_process.stdout = return_value
            mock_process.stderr = ""
            mock_process.returncode = return_code
            mock_subprocess_run.return_value = mock_process
            if is_error:
                mock_subprocess_run.side_effect = subprocess.CalledProcessError(
                    returncode=1, cmd="echo", output="error output", stderr="error"
                )

        return self.backend.request(**request_params)

    @mock.patch("subprocess.run")
    def test_request_success_backend_sync(self, mock_subprocess_run):
        request_data = self.common_request_data.get("version.get")
        result = self._request_backend_sync(
            request_params=request_data.get("request_params"),
            return_value=request_data.get("return_value"),
            mock_subprocess_run=mock_subprocess_run,
        )
        self.assertIsNotNone(result)
        response = result.get("response")
        self.assertIsNotNone(response)
        data = response.get("data")
        self.assertIsNotNone(data)
        self.assertIsNotNone(data.get("release"))
        self.assertEqual(result["status_code"], 0)
        self.assertTrue(result["success"])

    @mock.patch("subprocess.run")
    def test_request_failure_backend_sync(self, mock_subprocess_run):
        request_data = self.common_request_data.get("version.get")
        result = self._request_backend_sync(
            request_params=request_data.get("request_params"),
            return_value=request_data.get("return_value"),
            is_error=True,
            mock_subprocess_run=mock_subprocess_run,
        )
        self.assertIsNone(result["response"])
        self.assertEqual(result["status_code"], 1)
        self.assertFalse(result["success"])

    def test_request_no_command_backend_sync(self):
        # Test behavior when format_command returns None
        request_data = self.common_request_data.get("version.get")
        result = self._request_backend_sync(
            request_params=request_data.get("request_params"),
        )
        self.assertIsNone(result["response"])
        self.assertNotEqual(result["status_code"], 0)
        self.assertFalse(result["success"])


if __name__ == "__main__":
    unittest.main()
