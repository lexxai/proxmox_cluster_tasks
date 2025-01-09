import unittest
from importlib.metadata import entry_points
from unittest.mock import patch, MagicMock
import subprocess

from ext_api.backends.backend_registry import BackendRegistry
from ext_api.backends.registry import register_backends


class BackendRequestTest(unittest.TestCase):
    def setUp(self):
        # class MockBackend:
        # def format_command(self, endpoint, params, method, data, endpoint_params):
        #     # Simulate different commands based on the backend logic
        #     match endpoint:
        #         case "/version":
        #             return 'echo {"release":"8.3","repoid":"3e76eec21c4a14a7","version":"8.3.2"}'
        #         case _:
        #             return "mock_command"

        # def result_analyze(self, output, error, exit_status):
        #     # Simulate analyzing the result and returning a response
        #     return {
        #         "response": output,
        #         "status_code": exit_status,
        #         "success": exit_status == 0,
        #     }

        # self.backend = MockBackend()
        backend_name = "cli"
        register_backends(backend_name)
        backend_cls = BackendRegistry.get_backend(backend_name)
        self.backend = backend_cls(entry_point="echo")

    @patch("subprocess.run")
    def test_request_success_cli_backend_sync(self, mock_subprocess_run):
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
        # Mock a subprocess that raises CalledProcessError
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="mock_command", output="error output", stderr="error"
        )
        request_params = {
            "method": "get",
            "endpoint": "version",
        }
        result = self.backend.request(**request_params)
        self.assertIsNone(result["response"])
        self.assertEqual(result["status_code"], 1)
        self.assertFalse(result["success"])

    #
    # @patch("subprocess.run")
    # def test_request_no_command(self, mock_subprocess_run):
    #     # Test behavior when format_command returns None
    #     self.backend.format_command = lambda *args, **kwargs: None
    #     result = self.backend.request("GET", "/version")
    #     self.assertIsNone(result["response"])
    #     self.assertEqual(result["status_code"], -1)
    #     self.assertFalse(result["success"])


if __name__ == "__main__":
    unittest.main()
