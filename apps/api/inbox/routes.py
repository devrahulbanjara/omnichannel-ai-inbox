"""HTTP endpoints for conversations and messages."""

from fastapi import APIRouter, HTTPException

from inbox import store
from inbox.schemas import Conversation, Message, MessageCreate

router = APIRouter(prefix="/conversations", tags=["inbox"])


def get_conversation_or_404(conversation_id: str) -> Conversation:
    conversation = store.conversations.get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("")
def list_conversations() -> list[Conversation]:
    """All conversations, the most recently active first."""
    return sorted(store.conversations.values(), key=lambda c: c.last_message_at, reverse=True)


@router.get("/{conversation_id}/messages")
def list_messages(conversation_id: str) -> list[Message]:
    """The messages of one conversation, oldest first."""
    get_conversation_or_404(conversation_id)
    return store.messages[conversation_id]


@router.post("/{conversation_id}/messages", status_code=201)
def send_staff_reply(conversation_id: str, body: MessageCreate) -> Message:
    """A staff member replies to the customer."""
    conversation = get_conversation_or_404(conversation_id)
    message = Message(
        id=store.new_id(),
        conversation_id=conversation_id,
        direction="out",
        sender_type="staff",
        text=body.text,
        created_at=store.now(),
    )
    store.messages[conversation_id].append(message)
    conversation.last_message_at = message.created_at
    return message
