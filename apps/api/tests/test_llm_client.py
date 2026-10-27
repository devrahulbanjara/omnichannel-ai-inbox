import asyncio

import httpx2
import openai
import pytest
from pydantic import SecretStr

from app.core.config import settings
from app.llm.client import LLMClient, LLMError

HELLO = [{"role": "user", "content": "hi"}]


@pytest.fixture(autouse=True)
def fake_groq_key(monkeypatch):
    """The openai client refuses an empty key, and CI has no .env."""
    monkeypatch.setattr(settings, "groq_api_key", SecretStr("test-key"))


def fake_client(status: int, body: dict) -> LLMClient:
    """An LLMClient whose provider always answers with this status and JSON body."""
    client = LLMClient()
    transport = httpx2.MockTransport(lambda request: httpx2.Response(status, json=body))
    client.openai = openai.AsyncOpenAI(
        api_key="test-key",
        base_url="http://fake/v1",
        max_retries=0,
        http_client=httpx2.AsyncClient(transport=transport),
    )
    return client


def completion(message: dict) -> dict:
    return {
        "id": "c1",
        "object": "chat.completion",
        "created": 0,
        "model": "test-model",
        "choices": [{"index": 0, "finish_reason": "stop", "message": message}],
        "usage": {"prompt_tokens": 12, "completion_tokens": 3, "total_tokens": 15},
    }


def test_answer_returns_text_and_tokens():
    body = completion({"role": "assistant", "content": "Hello!"})

    result = asyncio.run(fake_client(200, body).generate(HELLO))

    assert result.text == "Hello!"
    assert (result.input_tokens, result.output_tokens) == (12, 3)


def test_tool_calls_are_returned():
    tool_call = {
        "id": "call_1",
        "type": "function",
        "function": {"name": "search_knowledge", "arguments": '{"query": "delivery"}'},
    }
    body = completion({"role": "assistant", "content": None, "tool_calls": [tool_call]})

    result = asyncio.run(fake_client(200, body).generate(HELLO))

    assert result.tool_calls[0].name == "search_knowledge"
    assert result.tool_calls[0].arguments == '{"query": "delivery"}'


def test_provider_error_raises_llm_error():
    client = fake_client(429, {"error": {"message": "slow down"}})

    with pytest.raises(LLMError):
        asyncio.run(client.generate(HELLO))
