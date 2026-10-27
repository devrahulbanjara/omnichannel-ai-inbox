import time
from dataclasses import dataclass

import openai
from loguru import logger
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

from app.core.config import settings


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str  # JSON text written by the model


@dataclass
class LLMResult:
    text: str | None
    tool_calls: list[ToolCall]
    input_tokens: int
    output_tokens: int
    latency_ms: int
    model: str


class LLMError(Exception):
    """The provider failed after its retries, or refused the request."""


class LLMClient:
    """Talks to a Groq model through Groq's OpenAI-compatible API.

    The openai package retries 429, 5xx, timeouts and connection errors with backoff.
    """

    def __init__(self) -> None:
        self.model = settings.groq_model
        self.openai = openai.AsyncOpenAI(
            base_url=settings.groq_base_url,
            api_key=settings.groq_api_key.get_secret_value(),
            timeout=settings.groq_timeout_seconds,
            max_retries=settings.groq_max_retries,
        )

    async def generate(
        self,
        messages: list[ChatCompletionMessageParam],
        tools: list[ChatCompletionToolParam] | None = None,
    ) -> LLMResult:
        started = time.monotonic()
        try:
            response = await self.openai.chat.completions.create(
                model=self.model, messages=messages, tools=tools or openai.omit
            )
        except openai.APIError as exc:
            raise LLMError(f"{self.model} failed: {exc}") from exc

        message = response.choices[0].message

        tool_calls = []
        for call in message.tool_calls or []:
            if call.type == "function":
                tool_calls.append(ToolCall(call.id, call.function.name, call.function.arguments))

        result = LLMResult(
            text=message.content,
            tool_calls=tool_calls,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
            latency_ms=round((time.monotonic() - started) * 1000),
            model=self.model,
        )
        logger.info(
            "{} answered: {} tokens in, {} out, {} ms",
            self.model,
            result.input_tokens,
            result.output_tokens,
            result.latency_ms,
        )
        return result
