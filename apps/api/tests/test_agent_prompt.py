import asyncio

from app.agent.prompts.conversation import conversation_prompt
from app.agent.prompts.fallback import SALES_ASSISTANT
from app.agent.prompts.system import fallback_prompt, load_system_prompt
from app.models import Message, Organization
from app.models.enums import SenderType


def make_message(sender_type: SenderType, text: str) -> Message:
    return Message(sender_type=sender_type, text=text)


def test_prompt_starts_with_system_prompt_naming_the_store():
    org = Organization(name="Kathmandu Bags")

    prompt = conversation_prompt(fallback_prompt(), org, [])

    assert prompt[0]["role"] == "system"
    assert "Kathmandu Bags" in str(prompt[0].get("content"))


def test_customer_is_user_and_store_side_is_assistant():
    org = Organization(name="Kathmandu Bags")
    messages = [
        make_message(SenderType.CUSTOMER, "Namaste"),
        make_message(SenderType.STAFF, "Hello! How can I help?"),
        make_message(SenderType.AI, "We have black suitcases."),
        make_message(SenderType.CUSTOMER, "Price?"),
    ]

    prompt = conversation_prompt(fallback_prompt(), org, messages)

    turns = []
    for turn in prompt[1:]:
        turns.append((turn["role"], turn.get("content")))
    assert turns == [
        ("user", "Namaste"),
        ("assistant", "Hello! How can I help?"),
        ("assistant", "We have black suitcases."),
        ("user", "Price?"),
    ]


def test_store_name_replaces_the_template_variable():
    org = Organization(name="Kathmandu Bags")

    prompt = conversation_prompt(fallback_prompt(), org, [])

    assert "{{store_name}}" in SALES_ASSISTANT
    assert "{{" not in str(prompt[0].get("content"))


def test_prompt_from_code_is_used_when_tracing_is_off():
    prompt = asyncio.run(load_system_prompt())

    assert prompt.is_fallback
    assert prompt.version == 0
    assert prompt.prompt == SALES_ASSISTANT
