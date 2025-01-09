import unittest
from unittest.mock import patch, MagicMock
import subprocess

from ext_api.backends.backend_registry import BackendRegistry
from ext_api.backends.registry import register_backends


class BackendRequestSSHTest(unittest.TestCase):
    def setUp(self):
        backend_name = "ssh"
        register_backends(backend_name)
        backend_cls = BackendRegistry.get_backend(backend_name)
        self.backend = backend_cls(
            entry_point="echo", hostname="localhost", username="fake_user"
        )

    @patch("subprocess.run")
    def test_request_success_ssh_backend_sync(self, mock_subprocess_run):
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
    def test_request_failure_ssh_backend_sync(self, mock_subprocess_run):
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

    def test_request_no_command_ssh_backend_sync(self):
        # Test behavior when format_command returns None
        request_params = {
            "method": "get",
            "endpoint": "",
        }
        result = self.backend.request(**request_params)
        self.assertIsNone(result["response"])
        self.assertEqual(result["status_code"], -1)
        self.assertFalse(result["success"])


# if __name__ == "__main__":
#     unittest.main()
