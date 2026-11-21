import asyncio

from langfuse.api import Prompt_Text
from langfuse.model import TextPromptClient
from loguru import logger

from app.agent.prompts.fallback import SALES_ASSISTANT
from app.core.config import settings
from app.llm.client import tracing

PROMPT_NAME = "sales-assistant"
PROMPT_LABEL = "production"  # the version Langfuse serves to the app
PROMPT_CACHE_SECONDS = 60  # after this, Langfuse refreshes the prompt in the background


def fallback_prompt() -> TextPromptClient:
    """The prompt from code, as version 0. Model calls made with it are not linked to a Langfuse version."""  # noqa: E501

    prompt = Prompt_Text(
        name=PROMPT_NAME,
        prompt=SALES_ASSISTANT,
        version=0,
        config={},
        labels=[],
        tags=[],
    )
    return TextPromptClient(prompt, is_fallback=True)


async def load_system_prompt() -> TextPromptClient:
    """The production version from Langfuse, cached. Falls back to the prompt from code."""

    if not settings.langfuse_tracing_enabled or not settings.langfuse_public_key:
        return fallback_prompt()

    # The SDK fetches synchronously, so it runs in a thread to keep the event loop free.
    prompt = await asyncio.to_thread(
        tracing.get_prompt,
        PROMPT_NAME,
        label=PROMPT_LABEL,
        cache_ttl_seconds=PROMPT_CACHE_SECONDS,
        fallback=SALES_ASSISTANT,
    )

    if prompt.is_fallback:
        logger.warning("Langfuse unreachable; using the {} prompt from code", PROMPT_NAME)
    return prompt
