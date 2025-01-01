import logging

from config.config import configuration
from cluster_tasks.ext_cli.handler import CLIHandler
from cluster_tasks.main import cluster_tasks

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
