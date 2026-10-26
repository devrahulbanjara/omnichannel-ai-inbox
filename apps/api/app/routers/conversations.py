import uuid

from fastapi import APIRouter

from app.dependencies import ConversationServiceDep, MessageServiceDep
from app.schemas.conversation import ConversationRead
from app.schemas.message import MessageCreate, MessageRead

router = APIRouter(prefix="/conversations", tags=["inbox"])


@router.get("")
async def list_conversations(conversations: ConversationServiceDep) -> list[ConversationRead]:
    return await conversations.list_recent()


@router.get("/{conversation_id}/messages")
async def list_messages(
    conversation_id: uuid.UUID,
    conversations: ConversationServiceDep,
    messages: MessageServiceDep,
) -> list[MessageRead]:
    conversation = await conversations.get(conversation_id)
    return await messages.list_for(conversation)


@router.post("/{conversation_id}/messages", status_code=201)
async def send_staff_reply(
    conversation_id: uuid.UUID,
    body: MessageCreate,
    conversations: ConversationServiceDep,
    messages: MessageServiceDep,
) -> MessageRead:
    conversation = await conversations.get(conversation_id)
    return await messages.send_staff_reply(conversation, body.text)
