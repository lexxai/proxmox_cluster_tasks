import copy
import unittest

from unittest import mock

from httpx import Response as httpx_Response

from config.config import ConfigLoader
from ext_api.backends.backend_registry import BackendRegistry
from ext_api.backends.registry import register_backends
from tests.conftest import export_mock_backend_settings


class BackendRequestHTTPSTest(unittest.TestCase):

    mock_backend_settings = None  # Explicitly declare the attribute

    common_request_data = {
        "version.get": {
            "request_params": {
                "method": "get",
                "endpoint": "version",
            },
            "return_value": '{"data": {"release":"8.3","repoid":"3e76eec21c4a14a7","version":"8.3.2"}}',
            "return_code": 200,
        }
    }

    def setUp(self):
        self.mock_backend_settings = export_mock_backend_settings()
        backend_name = "https"
        register_backends(backend_name)
        backend_cls = BackendRegistry.get_backend(backend_name)
        if self.mock_backend_settings.get(backend_name.upper()):
            backend = backend_cls(
                base_url="https://fake_url:8006",
                entry_point="/api2/json",
                token="fake_token",
            )
        else:
            # Use Real Configuration
            configuration = ConfigLoader()
            backend = backend_cls(
                base_url=configuration.get("API.BASE_URL"),
                entry_point=configuration.get("API.ENTRY_POINT"),
                token=configuration.get("API.TOKEN"),
            )

        if self.mock_backend_settings.get(backend_name.upper()):
            if hasattr(backend, "connect"):
                mock_connect = mock.MagicMock()
                backend._client = mock.MagicMock()
                mock.patch.object(backend, "connect", side_effect=mock_connect)

        self.backend = backend
        self.backend_name = backend_name

    def _request_backend_sync(
        self,
        request_params=None,
        return_value=None,
        return_code: int = 200,
        is_error: bool = False,
    ):
        if self.mock_backend_settings.get(self.backend_name.upper(), True):
            mock_response = httpx_Response(status_code=return_code, text=return_value)

            def mock_request(method, url, data=None, params=None, *args, **kwargs):
                # print("mock_exec", command)
                if is_error:
                    raise Exception(  # Simulate an SSH error
                        "run mocked request '{}' failed with return code {}: {}".format(
                            url, 400, "mock error output"
                        )
                    )
                return mock_response

            client = mock.patch.object(
                self.backend.client, "request", side_effect=mock_request
            )
        else:
            client = self.backend
            if is_error:
                request_params = request_params.copy()
                request_params["endpoint"] = None

        with client:
            result = self.backend.request(**request_params)

        return result

    def test_request_success_backend_sync(self):
        request_data = self.common_request_data.get("version.get")
        result = self._request_backend_sync(
            request_params=request_data.get("request_params"),
            return_value=request_data.get("return_value"),
        )
        self.assertIsNotNone(result)
        response = result.get("response")
        data = response.get("data")
        self.assertIsNotNone(data)
        self.assertIsNotNone(data.get("release"))
        self.assertEqual(result["status_code"], request_data.get("return_code"))
        self.assertTrue(result["success"])

    def test_request_failure_backend_sync(self):
        request_data = self.common_request_data.get("version.get")
        result = self._request_backend_sync(
            request_params=request_data.get("request_params"),
            return_value=request_data.get("return_value"),
            is_error=True,
        )
        self.assertIsNotNone(result["response"])
        self.assertNotEqual(result["status_code"], request_data.get("return_code"))
        self.assertFalse(result["success"])

    def test_request_no_command_backend_sync(self):
        # Test behavior when format_command returns None

        request_data = copy.deepcopy(self.common_request_data.get("version.get"))
        request_data["request_params"]["endpoint"] = ""
        result = self._request_backend_sync(
            request_params=request_data.get("request_params"),
        )
        self.assertIsNotNone(result["response"])
        self.assertNotEqual(result["status_code"], request_data.get("return_code"))
        self.assertFalse(result["success"])


if __name__ == "__main__":
    unittest.main()
