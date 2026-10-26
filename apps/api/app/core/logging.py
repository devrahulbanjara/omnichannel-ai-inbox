import sys

from loguru import logger

FORMAT = (
    "<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | "
    "<cyan>{extra[request_id]}</cyan> | {message}"
)


def configure_logging(level: str, json: bool) -> None:
    """Plain-text log lines, or one JSON object per line when `json` is true."""
    logger.remove()
    logger.configure(extra={"request_id": "-"})  # outside a request
    logger.add(sys.stdout, level=level, format=FORMAT, serialize=json)
