import logging

from config.config import configuration


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


def config_logger(logger: logging):
    # Setup colored logger
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel("DEBUG" if configuration.get("DEBUG") else "INFO")
    return logger
