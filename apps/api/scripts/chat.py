"""Chat with the configured LLM from the terminal: `uv run python -m scripts.chat`."""

import asyncio
import contextlib

from openai.types.chat import ChatCompletionMessageParam

from app.llm.client import LLMClient, LLMError


async def main() -> None:
    client = LLMClient()
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": "You are a helpful assistant. Answer briefly."}
    ]
    while True:
        text = input("you> ").strip()
        if not text:
            continue
        messages.append({"role": "user", "content": text})
        try:
            result = await client.generate(messages)
        except LLMError as exc:
            print(f"error: {exc}")
            messages.pop()
            continue
        messages.append({"role": "assistant", "content": result.text})
        print(f"ai> {result.text}")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt, EOFError):  # Ctrl+C or Ctrl+D quits
        asyncio.run(main())
