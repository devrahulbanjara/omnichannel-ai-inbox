"""Chat with the AI as a customer of the first demo store: `uv run python -m scripts.chat`."""

import asyncio
import contextlib

from openai.types.chat import ChatCompletionMessageParam

from app.agent.loop import Agent
from app.agent.prompts.system import load_system_prompt
from app.agent.tools.base import ToolContext
from app.agent.tools.search_products import SearchProductsTool
from app.core.database import SessionLocal
from app.llm.client import LLMClient, LLMError, tracing
from app.services.organization import OrganizationService


async def main() -> None:
    client = LLMClient()
    tools = [SearchProductsTool()]
    agent = Agent(client, tools)

    async with SessionLocal() as session:
        organization_service = OrganizationService(session)
        org = await organization_service.get_current()
    print(f"Chatting as a customer of {org.name} (Ctrl+C quits)")

    system_prompt = await load_system_prompt()
    system_text = system_prompt.compile(store_name=org.name)
    messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": system_text}]
    while True:
        text = input("you> ").strip()
        if not text:
            continue
        messages_before = len(messages)
        messages.append({"role": "user", "content": text})
        try:
            async with SessionLocal() as session:  # a fresh session per turn sees current stock
                context = ToolContext(session=session, org=org)
                answer = await agent.reply(messages, context, system_prompt)
        except LLMError as exc:
            print(f"error: {exc}")
            del messages[messages_before:]  # forget the failed turn
            continue
        print(f"ai> {answer}")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt, EOFError):  # Ctrl+C or Ctrl+D quits
        asyncio.run(main())
    tracing.flush()  # send the last traces before the process exits
