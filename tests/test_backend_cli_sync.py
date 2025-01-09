import unittest
from unittest.mock import patch, MagicMock
import subprocess

import pytest

from ext_api.backends.backend_registry import BackendRegistry
from ext_api.backends.registry import register_backends


class BackendRequestCLITest(unittest.TestCase):

    def setUp(self):
        # self.mock_backend_settings = {"HTTPS": True, "SSH": True, "CLI": False}
        backend_name = "cli"
        register_backends(backend_name)
        backend_cls = BackendRegistry.get_backend(backend_name)
        self.backend = backend_cls(entry_point="echo")

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, request):
        # Store the fixture value for use in tests
        self.mock_backend_settings = request.getfixturevalue("mock_backend_settings")

    @patch("subprocess.run")
    def test_request_success_cli_backend_sync(self, mock_subprocess_run):
        if self.mock_backend_settings.get("CLI", True):
            # Mock a successful subprocess run
            mock_process = MagicMock()
            mock_process.stdout = (
                '{"release":"8.3","repoid":"3e76eec21c4a14a7","version":"8.3.2"}'
            )
            mock_process.stderr = ""
            mock_process.returncode = 0
            mock_subprocess_run.return_value = mock_process

        request_params = {
            "method": "get",
            "endpoint": "version",
        }
        result = self.backend.request(**request_params)
        self.assertIsNotNone(result)
        response = result.get("response")
        self.assertIsNotNone(response)
        data = response.get("data")
        self.assertIsNotNone(data)
        self.assertIsNotNone(data.get("release"))
        self.assertEqual(result["status_code"], 0)
        self.assertTrue(result["success"])

    @patch("subprocess.run")
    def test_request_failure_cli_backend_sync(self, mock_subprocess_run):
        if self.mock_backend_settings.get("CLI", True):
            # Mock a subprocess that raises CalledProcessError
            mock_subprocess_run.side_effect = subprocess.CalledProcessError(
                returncode=1, cmd="echo", output="error output", stderr="error"
            )
        request_params = {
            "method": "get",
            "endpoint": "version",
        }
        result = self.backend.request(**request_params)
        self.assertIsNone(result["response"])
        self.assertEqual(result["status_code"], 1)
        self.assertFalse(result["success"])

    def test_request_no_command_cli_backend_sync(self):
        # Test behavior when format_command returns None
        request_params = {
            "method": "get",
            "endpoint": "",
        }
        result = self.backend.request(**request_params)
        self.assertIsNone(result["response"])
        self.assertEqual(result["status_code"], -1)
        self.assertFalse(result["success"])


if __name__ == "__main__":
    unittest.main()
