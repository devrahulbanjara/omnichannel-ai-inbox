import uuid
from datetime import UTC, datetime, timedelta

from inbox.schemas import Conversation, Message

conversations: dict[str, Conversation] = {}
messages: dict[str, list[Message]] = {}  # conversation id → its messages, oldest first


def new_id() -> str:
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.now(UTC)


def reset() -> None:
    """Empty the store and add two demo conversations."""
    conversations.clear()
    messages.clear()
    demo = [
        ("Sujan Maharjan", "Do you have the 24-inch suitcase in black?", 30),
        ("Anisha Karki", "What is the price of the travel backpack?", 5),
    ]
    for name, text, minutes_ago in demo:
        at = now() - timedelta(minutes=minutes_ago)
        conversation = Conversation(
            id=new_id(),
            contact_name=name,
            channel="rahulcoolgram",
            status="open",
            last_message_at=at,
        )
        conversations[conversation.id] = conversation
        messages[conversation.id] = [
            Message(
                id=new_id(),
                conversation_id=conversation.id,
                direction="in",
                sender_type="contact",
                text=text,
                created_at=at,
            )
        ]


reset()
