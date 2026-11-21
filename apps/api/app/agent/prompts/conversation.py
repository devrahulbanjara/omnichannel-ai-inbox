from langfuse.model import TextPromptClient
from openai.types.chat import ChatCompletionMessageParam

from app.models import Message, Organization
from app.models.enums import SenderType


def conversation_prompt(
    system_prompt: TextPromptClient, org: Organization, messages: list[Message]
) -> list[ChatCompletionMessageParam]:
    """The model's input: the system prompt, then every message of the conversation.

    Customer messages become "user" turns. Staff and AI messages both speak for the store,
    so they become "assistant" turns.
    """

    system_text = system_prompt.compile(store_name=org.name)

    prompt: list[ChatCompletionMessageParam] = [{"role": "system", "content": system_text}]

    for message in messages:
        if message.sender_type == SenderType.CUSTOMER:
            prompt.append({"role": "user", "content": message.text})
        else:
            prompt.append({"role": "assistant", "content": message.text})

    return prompt
