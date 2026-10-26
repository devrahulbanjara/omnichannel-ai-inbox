import pytest
from fastapi.testclient import TestClient

from inbox import store
from main import app


@pytest.fixture(autouse=True)
def fresh_store():
    """Every test starts with the same two demo conversations."""
    store.reset()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
