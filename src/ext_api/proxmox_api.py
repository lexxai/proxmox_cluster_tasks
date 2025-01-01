import logging

from nacl.pwhash.argon2i import verify

from config.config import configuration
from ext_api.backends.backend_abstract import ProxmoxBackend
from ext_api.backends.registry import register_backends
from ext_api.backends.backend_registry import (
    BackendRegistry,
    BackendType,
)

logger = logging.getLogger(f"CT.{__name__}")


class ProxmoxAPI:
    def __init__(
        self,
        backend: ProxmoxBackend | None = None,
        backend_type: str | BackendType | None = BackendType.SYNC,
        backend_name: str = "https",
        **kwargs,
    ):
        try:
            self.backend_type = (
                BackendType(backend_type.strip().lower())
                if isinstance(backend_type, str)
                else backend_type
            )
        except ValueError:
            raise ValueError(
                f"Unsupported backend type: {backend_type}, available: {[k.lower() for k in BackendType.__members__]}"
            )
        self.backend_name = backend_name.strip().lower() if backend_name else None
        # Verify backend_name is registered
        if backend is not None:
            backend_name, backend_type = BackendRegistry.get_name_type(backend)
            if all([backend_name, backend_type]):
                self.backend_name = backend_name
                self.backend_type = backend_type
                self._backend = backend
        else:
            self._backend = self._create_backend(**kwargs)

    def _create_backend(self, **kwargs) -> ProxmoxBackend:
        """Factory method to create the appropriate backend."""
        logger.debug(
            f"Creating backend: {self.backend_name} of type: {self.backend_type}"
        )
        match self.backend_name:
            case "https":
                verify_ssl: bool = kwargs.get(
                    "verify_ssl", configuration.get("API.VERIFY_SSL")
                )
                params = {
                    "base_url": kwargs.get("base_url")
                    or configuration.get("API.BASE_URL"),
                    "entry_point": kwargs.get("entry_point")
                    or configuration.get("API.ENTRY_POINT"),
                    "token": kwargs.get("token") or configuration.get("API.TOKEN"),
                    "verify_ssl": verify_ssl,
                }
            case "cli":
                params = {
                    "entry_point": kwargs.get("entry_point")
                    or configuration.get("CLI.ENTRY_POINT"),
                }
            case "ssh":
                params = {
                    "entry_point": kwargs.get("entry_point")
                    or configuration.get("CLI.ENTRY_POINT"),
                    "hostname": kwargs.get("hostname")
                    or configuration.get("SSH.HOSTNAME"),
                    "username": kwargs.get("username")
                    or configuration.get("SSH.USERNAME"),
                    "password": kwargs.get("password")
                    or configuration.get("SSH.PASSWORD"),
                    "port": kwargs.get("port") or configuration.get("SSH.PORT"),
                    "key_filename": kwargs.get("key_filename")
                    or configuration.get("SSH.KEY_FILENAME"),
                    "agent": kwargs.get("agent", configuration.get("SSH.AGENT")),
                }
            case _:
                params = {}

        backend_cls: type[ProxmoxBackend] = BackendRegistry.get_backend(
            self.backend_name, self.backend_type
        )
        if backend_cls:
            kwargs.update(params)
            return backend_cls(**kwargs)
        raise ValueError(
            f"Unsupported backend: {self.backend_name} of this type: {self.backend_type}"
        )

    def __enter__(self):
        """Enter context for synchronous backends."""
        if self.backend_type != BackendType.SYNC:
            raise RuntimeError("Use 'async with' for asynchronous backends.")
        if hasattr(self._backend, "__enter__"):
            self._backend.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context for synchronous backends."""
        if self.backend_type == BackendType.SYNC:
            if hasattr(self._backend, "__exit__"):
                self._backend.__exit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self):
        """Enter context for asynchronous backends."""
        if self.backend_type != BackendType.ASYNC:
            raise RuntimeError("Use 'with' for synchronous backends.")
        if hasattr(self._backend, "__aenter__"):
            await self._backend.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context for asynchronous backends."""
        if self.backend_type == BackendType.ASYNC:
            if hasattr(self._backend, "__aexit__"):
                await self._backend.__aexit__(exc_type, exc_val, exc_tb)

    def request(self, *args, **kwargs):
        """Make a synchronous request."""
        if self.backend_type != "sync":
            raise RuntimeError("This instance is configured for asynchronous requests.")
        return self._backend.request(*args, **kwargs)

    async def async_request(self, *args, **kwargs):
        """Make an asynchronous request."""
        if self.backend_type != "async":
            raise RuntimeError("This instance is configured for synchronous requests.")
        return await self._backend.async_request(*args, **kwargs)


class ProxmoxSSHBackend:
    pass


# TEST JUST
if __name__ == "__main__":
    import asyncio

    logger = logging.getLogger("CT")
    logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")

    class ColoredFormatter(logging.Formatter):
        # Define color codes
        COLORS = {
            "DEBUG": "\033[94m",  # Blue
            "INFO": "\033[92m",  # Green
            "ERROR": "\033[91m",  # Red
            "RESET": "\033[0m",  # Reset color
        }

        def format(self, record):
            log_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
            message = super().format(record)
            return f"{log_color}{message}{self.COLORS['RESET']}"

    # Setup colored logger
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)
    # logger.addHandler(logging.StreamHandler())

    node = configuration.get("NODES", [])[0]

    # Register backend with the registry
    try:
        register_backends()

        # backend = None
        # Now you can use ProxmoxAPI with the backend you registered
        # backend = BackendRegistry.get_backend("https", backend_type=BackendType.SYNC)

        api = ProxmoxAPI(backend_name="cli")

        with api as proxmox:
            response = proxmox.request("get", "version")
            logger.info(response)
            # response = proxmox.request(
            #     "create",
            #     "/cluster/ha/groups",
            #     params={"node": node},
            #     data={"name": "test-node"},
            # )
            # logger.info(response)

    except Exception as e:
        logger.error(f"ERROR: {e}")

    logger.info("\n\nTESTING ASYNC --------\n")

    async def async_main():
        # Register backend with the registry

        try:
            # Now you can use ProxmoxAPI with the backend you registered
            api = ProxmoxAPI(
                backend_type="async",
                backend_name="ssh",
            )
            # response = await api.async_request("get", "version")
            # logger.info(response)

            async with api as proxmox:
                response = await proxmox.async_request("get", "version")
                logger.info(response)
                # response = await proxmox.async_request(
                #     "post",
                #     "/cluster/ha/groups",
                #     params={},
                #     data={"group": "test-group", "nodes": "c01:100,c02,c03"},
                # )
                # logger.info(response)
                # response = await proxmox.async_request(
                #     "get",
                #     "/cluster/ha/groups",
                #     params={},
                # )
                # logger.info(response)
        except Exception as e:
            logger.error(f"ERROR: {e}")

    asyncio.run(async_main())
