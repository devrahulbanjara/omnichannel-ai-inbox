from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Message


class MessageService:
    """Message queries and writes."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for(self, conversation: Conversation) -> list[Message]:
        """Messages in chronological order."""
        result = await self.session.scalars(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        )
        return list(result)

    async def send_staff_reply(self, conversation: Conversation, text: str) -> Message:
        message = conversation.reply_as_staff(text)
        self.session.add(message)
        await self.session.commit()  # message and conversation update in one transaction
        return message
