import sys

from loguru import logger

FORMAT = (
    "<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | "
    "<cyan>{extra[request_id]}</cyan> | {message}"
)


def configure_logging(level: str, json: bool) -> None:
    """Readable lines for local dev; one JSON object per line when `json` is on (production)."""
    logger.remove()  # drop loguru's default output
    logger.configure(extra={"request_id": "-"})  # shown when we're outside a request
    logger.add(sys.stdout, level=level, format=FORMAT, serialize=json)
