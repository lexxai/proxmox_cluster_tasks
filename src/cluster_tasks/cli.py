import logging

from config_loader.config import configuration
from old.ext_cli import CLIHandler
from main import cluster_tasks

logger = logging.getLogger("CT")


def cli():
    cluster_tasks(CLIHandler())


def main():
    logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
    logger.addHandler(logging.StreamHandler())
    logger.info("CLI Main")
    cli()


if __name__ == "__main__":
    main()
