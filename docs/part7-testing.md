## Testing

This project uses pytest for testing, with all test files located in the tests folder.

### Installing Pytest
You can install pytest and other dependencies either using Poetry or pip:

#### Using Poetry
To install the development dependencies with Poetry, run:

```bash 
poetry install --with dev
````
#### Using Pip
To install pytest and the necessary plugins using pip, run:

```bash
pip install pytest pytest-mock pytest-asyncio
````

### Configuring Tests
To customize test behavior, you can configure environment variables before running tests. The following variables control which backend mock implementations are used:

```plain
MOCK_BACKEND_HTTPS=true
MOCK_BACKEND_SSH=true
MOCK_BACKEND_CLI=true
```
- If a value is set to true or not set, the corresponding backend (HTTPS, SSH, or CLI) will use predefined fake/mock data during the tests instead of real interactions.
- If the value is false, the tests will use real data or connections where applicable. 

You can set these variables in your terminal before running tests:
```bash
export MOCK_BACKEND_HTTPS=true
export MOCK_BACKEND_SSH=false
export MOCK_BACKEND_CLI=true
```
Alternatively, you can define them in a .env file if supported by your environment setup.


### Running Tests
To execute the tests, simply run:
```bash
pytest
```
Example Output:
```bash
======================================================= test session starts =======================================================
platform darwin -- Python 3.12.8, pytest-8.3.4, pluggy-1.5.0
rootdir: /Users/lex/PycharmProjects/proxmox_cluster_tasks
configfile: pyproject.toml
plugins: anyio-4.7.0, mock-3.14.0, asyncio-0.25.1
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=function
collected 18 items                                                                                                                

tests/test_api.py::test_api_version_https[get_api0] PASSED                                                                  [  5%]
tests/test_api.py::test_api_version_ssh[get_api0] PASSED                                                                    [ 11%]
tests/test_api.py::test_api_version_cli[get_api0] PASSED                                                                    [ 16%]
tests/test_api.py::test_api_version_https_async[get_api_async0] PASSED                                                      [ 22%]
tests/test_api.py::test_api_version_ssh_async[get_api_async0] PASSED                                                        [ 27%]
tests/test_api.py::test_api_version_cli_async[get_api_async0] PASSED                                                        [ 33%]
tests/test_backend_cli_sync.py::BackendRequestCLITest::test_request_failure_backend_sync PASSED                             [ 38%]
tests/test_backend_cli_sync.py::BackendRequestCLITest::test_request_no_command_backend_sync PASSED                          [ 44%]
tests/test_backend_cli_sync.py::BackendRequestCLITest::test_request_success_backend_sync PASSED                             [ 50%]
tests/test_backend_https_async.py::BackendRequestHTTPSTestAsync::test_request_failure_backend_async PASSED                  [ 55%]
tests/test_backend_https_async.py::BackendRequestHTTPSTestAsync::test_request_no_command_backend_async PASSED               [ 61%]
tests/test_backend_https_async.py::BackendRequestHTTPSTestAsync::test_request_success_backend_async PASSED                  [ 66%]
tests/test_backend_https_sync.py::BackendRequestHTTPSTest::test_request_failure_backend_sync PASSED                         [ 72%]
tests/test_backend_https_sync.py::BackendRequestHTTPSTest::test_request_no_command_backend_sync PASSED                      [ 77%]
tests/test_backend_https_sync.py::BackendRequestHTTPSTest::test_request_success_backend_sync PASSED                         [ 83%]
tests/test_backend_ssh_sync.py::BackendRequestSSHTest::test_request_failure_backend_sync PASSED                             [ 88%]
tests/test_backend_ssh_sync.py::BackendRequestSSHTest::test_request_no_command_backend_sync PASSED                          [ 94%]
tests/test_backend_ssh_sync.py::BackendRequestSSHTest::test_request_success_backend_sync PASSED                             [100%]

======================================================= 18 passed in 0.27s ========================================================
```
