from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.loop import Agent
from app.agent.postprocessing.reply import postprocess_reply
from app.agent.prompts.conversation import conversation_prompt
from app.agent.prompts.system import load_system_prompt
from app.agent.tools.base import ToolContext
from app.llm.client import LLMError
from app.models import Conversation, Message, Organization
from app.services.message import MessageService


class AgentReplyService:
    """Runs the AI agent on a conversation and sends its answer to the customer."""

    def __init__(self, session: AsyncSession, agent: Agent) -> None:
        self.session = session
        self.agent = agent

    async def reply_to(self, conversation: Conversation) -> Message | None:
        """Answer the conversation's last message. Returns None if the model gave no answer;
        the customer's message stays saved and staff can reply."""

        org = await self.session.get_one(Organization, conversation.org_id)
        message_service = MessageService(self.session)

        history = await message_service.list_for(conversation)
        system_prompt = await load_system_prompt()
        messages = conversation_prompt(system_prompt, org, history)
        context = ToolContext(session=self.session, org=org)

        try:
            answer = await self.agent.reply(messages, context, system_prompt)
        except LLMError as exc:
            logger.error("No AI reply for conversation {}: {}", conversation.id, exc)
            return None

        reply_text = postprocess_reply(answer)

        if not reply_text:
            logger.warning("Empty answer for conversation {}", conversation.id)
            return None

        return await message_service.send_ai_reply(conversation, reply_text)
