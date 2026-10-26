"""Write the API schema to openapi.json: `uv run python -m scripts.export_openapi`."""

import json
from pathlib import Path

from loguru import logger

from app.main import app

OUTPUT = Path(__file__).parent.parent / "openapi.json"


def main() -> None:
    OUTPUT.write_text(json.dumps(app.openapi(), indent=2) + "\n")
    logger.info("Wrote {}", OUTPUT)


if __name__ == "__main__":
    main()
