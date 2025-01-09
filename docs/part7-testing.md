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

### Running Tests
To execute the tests, simply run:
```bash
pytest
```
Example Output:
```bash
platform darwin -- Python 3.12.8, pytest-8.3.4, pluggy-1.5.0
rootdir: /Users/lex/PycharmProjects/proxmox_cluster_tasks
configfile: pyproject.toml
plugins: anyio-4.7.0, mock-3.14.0, asyncio-0.25.1
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None
collected 9 items                                                                                                                 

tests/test_api.py ......                                    [ 66%]
tests/test_backend_cli_sync.py ...                          [100%]

===================== 9 passed in 7.43s ===========================
```
