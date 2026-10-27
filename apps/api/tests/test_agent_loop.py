import asyncio

from openai.types.chat import ChatCompletionMessageParam

from app.agent.loop import GAVE_UP_REPLY, MAX_STEPS, Agent
from app.agent.tools.base import ToolContext
from app.agent.tools.search_products import SearchProductsTool
from app.core.database import SessionLocal
from app.llm.client import LLMClient, LLMResult, ToolCall
from app.services.organization import OrganizationService


class ScriptedLLM(LLMClient):
    """Returns prepared results in order and records the messages it was sent."""

    def __init__(self, results: list[LLMResult]) -> None:
        self.results = results
        self.sent: list[list[ChatCompletionMessageParam]] = []

    async def generate(self, messages, tools=None) -> LLMResult:
        self.sent.append(list(messages))
        return self.results.pop(0)


def answer(text: str) -> LLMResult:
    return LLMResult(text, [], 0, 0, 0, "scripted")


def asks_for(name: str, arguments: str) -> LLMResult:
    return LLMResult(None, [ToolCall("call_1", name, arguments)], 0, 0, 0, "scripted")


def run_agent(llm: ScriptedLLM) -> tuple[str, list[ChatCompletionMessageParam]]:
    async def run():
        async with SessionLocal() as session:
            organization_service = OrganizationService(session)
            org = await organization_service.get_current()
            context = ToolContext(session=session, org=org)
            messages: list[ChatCompletionMessageParam] = [
                {"role": "user", "content": "Black suitcase?"}
            ]
            tools = [SearchProductsTool()]
            agent = Agent(llm, tools)
            reply = await agent.reply(messages, context)
            return reply, messages

    return asyncio.run(run())


def test_text_answer_needs_no_tools():
    llm = ScriptedLLM([answer("Hello!")])

    reply, messages = run_agent(llm)

    assert reply == "Hello!"
    assert messages[-1] == {"role": "assistant", "content": "Hello!"}


def test_tool_result_is_sent_back_to_the_model():
    llm = ScriptedLLM(
        [asks_for("search_products", '{"query": "black suitcase"}'), answer("Yes, Rs 5,900.")]
    )

    reply, messages = run_agent(llm)

    assert reply == "Yes, Rs 5,900."
    tool_message = llm.sent[1][-1]
    assert tool_message["role"] == "tool"
    assert "Rs 5,900" in str(tool_message.get("content"))
    roles = []
    for message in messages:
        roles.append(message["role"])
    assert roles == ["user", "assistant", "tool", "assistant"]


def test_unknown_tool_is_reported_to_the_model():
    llm = ScriptedLLM([asks_for("delete_everything", "{}"), answer("Sorry.")])

    run_agent(llm)

    assert "Unknown tool delete_everything" in str(llm.sent[1][-1].get("content"))


def test_stops_after_max_steps():
    results = []
    for _ in range(MAX_STEPS):
        results.append(asks_for("search_products", '{"query": "bag"}'))
    llm = ScriptedLLM(results)

    reply, _messages = run_agent(llm)

    assert reply == GAVE_UP_REPLY
    assert len(llm.sent) == MAX_STEPS
