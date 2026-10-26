import json

from app.main import app
from scripts.export_openapi import OUTPUT


def test_openapi_file_matches_the_code():
    saved = json.loads(OUTPUT.read_text())

    assert saved == app.openapi(), (
        "openapi.json is out of date: run `uv run python -m scripts.export_openapi`"
    )
