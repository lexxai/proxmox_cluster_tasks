import argparse
import asyncio
import logging

from cluster_tasks.configure_logging import config_logger
from controller_sync import main as controller_sync
from controller_async import main as controller_async

logger = logging.getLogger("CT")


def main():
    controller_sync()


async def async_main():
    await controller_async()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("Proxmox Cluster Tasks")
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
    args = arg_parser.parse_args()
    if args.debug.lower() == "true":
        args.debug = True
    elif args.debug.lower() == "false":
        args.debug = False
    else:
        args.debug = None
    config_logger(logger, debug=args.debug)
    try:
        if args.sync:
            main()
        else:
            asyncio.run(async_main())
    except ValueError as e:
        logger.error(f"MAIN: {e}")
