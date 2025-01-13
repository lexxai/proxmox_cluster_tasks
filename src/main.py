import argparse
import asyncio
import logging
import os
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
# sys.path.insert(1, str(Path(__file__).parent.parent))

from cluster_tasks.configure_logging import config_logger
from cluster_tasks.controller_sync import main as controller_sync
from cluster_tasks.controller_async import main as controller_async
from config import config

try:
    from __version__ import __version__
except ImportError:
    __version__ = "unknown"

logger = logging.getLogger("CT")


def get_version():
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    if pyproject.exists() is False:
        return __version__
    init_file = Path(__file__).parent / "__version__.py"
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    version = data["tool"]["poetry"]["version"]
    if __version__ != version:
        with init_file.open("w") as f:
            f.write(f'__version__ = "{version}"')
    return version


def main(cli_args=None, **kwargs):
    controller_sync(cli_args)


async def async_main(cli_args=None, **kwargs):
    await controller_async(cli_args)


def cli():
    config_folder = config.configuration.config_folder
    project_name = "Proxmox Cluster Tasks"
    arg_parser = argparse.ArgumentParser(project_name)
    arg_parser.add_argument(
        "--debug",
        type=str,  # Accept as a string to parse custom logic
        choices=["true", "false", "none"],  # Allow specific values
        default="none",  # Default state
        help="Enable or disable debug mode (true, false, none)",
    )
    arg_parser.add_argument(
        "--sync", help="Run in sync mode, default is async mode", action="store_true"
    )
    arg_parser.add_argument(
        "--concurrent",
        help="Run scenarios concurrently; defaults to running sequentially.",
        action="store_true",
    )
    arg_parser.add_argument(
        "--config_file",
        help=f"Configuration file path, default is 'configs/config.toml'",
        default=None,
        type=Path,
    )
    arg_parser.add_argument(
        "--scenarios_config_file",
        help=f"Configuration file path for scenarios, default is 'configs/scenarios_configs.yaml'",
        default=config_folder / "scenarios_configs.yaml",
        type=Path,
    )
    arg_parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
    )

    args = arg_parser.parse_args()
    if args.debug.lower() == "true":
        args.debug = True
    elif args.debug.lower() == "false":
        args.debug = False
    else:
        args.debug = None
    config_logger(logger, debug=args.debug)

    if args.config_file:
        if not config.initialize(args.config_file):
            exit(1)

    cli_args = vars(args)
    try:
        if args.sync:
            main(cli_args=cli_args)
        else:
            asyncio.run(async_main(cli_args=cli_args))
        logger.info(f"{project_name}: Finished")
    except KeyboardInterrupt:
        logger.info(f"{project_name}: KeyboardInterrupt")
    except ValueError as e:
        logger.error(f"{project_name}: {e}")


if __name__ == "__main__":
    cli()