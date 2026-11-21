"""Upload the system prompt to Langfuse as a new production version, if it changed.

Usage: uv run python -m scripts.push_prompts "what changed"
"""

import sys

from loguru import logger

from app.agent.prompts.fallback import SALES_ASSISTANT
from app.agent.prompts.system import PROMPT_LABEL, PROMPT_NAME
from app.llm.client import tracing


def push_system_prompt(commit_message: str) -> None:
    current = None
    try:
        current = tracing.get_prompt(PROMPT_NAME, label=PROMPT_LABEL, cache_ttl_seconds=0)
    except Exception:  # the SDK raises a generic error when the prompt does not exist yet
        logger.info("{} does not exist in Langfuse yet", PROMPT_NAME)

    if current is not None and current.prompt == SALES_ASSISTANT:
        logger.info("{} is unchanged (version {})", PROMPT_NAME, current.version)
        return

    created = tracing.create_prompt(
        name=PROMPT_NAME,
        prompt=SALES_ASSISTANT,
        labels=[PROMPT_LABEL],
        commit_message=commit_message,
    )
    logger.info("{} version {} is now {}", PROMPT_NAME, created.version, PROMPT_LABEL)


if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "Update from code"
    push_system_prompt(message)
