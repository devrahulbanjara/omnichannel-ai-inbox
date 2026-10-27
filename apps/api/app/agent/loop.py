from collections.abc import Sequence

from loguru import logger
from openai.types.chat import (
    ChatCompletionMessageFunctionToolCallParam,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)

from app.agent.tools.base import Tool, ToolContext
from app.llm.client import LLMClient, ToolCall

MAX_STEPS = 5  # model calls per reply; stops a model that keeps calling tools
GAVE_UP_REPLY = "Sorry, I could not find that. A staff member will get back to you."


class Agent:
    """Answers with the help of tools: ask the model, run the tools it asks for,
    send their results back, and repeat until it answers in text."""

    def __init__(self, client: LLMClient, tools: Sequence[Tool]) -> None:
        self.client = client
        self.tools: dict[str, Tool] = {}
        for tool in tools:
            self.tools[tool.name] = tool

    async def reply(self, messages: list[ChatCompletionMessageParam], context: ToolContext) -> str:
        """The answer to the last message. Appends the model's tool calls, the tool results
        and the answer to `messages`."""
        definitions: list[ChatCompletionToolParam] = []
        for tool in self.tools.values():
            definitions.append(tool.definition())

        for _step in range(MAX_STEPS):
            result = await self.client.generate(messages, definitions)
            if not result.tool_calls:
                answer = result.text or ""
                messages.append({"role": "assistant", "content": answer})
                return answer

            # The model's request must come before the results, so it can match them up by id.
            tool_call_params: list[ChatCompletionMessageFunctionToolCallParam] = []
            for call in result.tool_calls:
                tool_call_params.append(
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {"name": call.name, "arguments": call.arguments},
                    }
                )
            messages.append(
                {"role": "assistant", "content": result.text, "tool_calls": tool_call_params}
            )
            for call in result.tool_calls:
                output = await self.run_tool(call, context)
                messages.append({"role": "tool", "tool_call_id": call.id, "content": output})

        logger.warning("No answer after {} steps", MAX_STEPS)
        messages.append({"role": "assistant", "content": GAVE_UP_REPLY})
        return GAVE_UP_REPLY

    async def run_tool(self, call: ToolCall, context: ToolContext) -> str:
        tool = self.tools.get(call.name)
        if tool is None:
            tool_names = ", ".join(self.tools)
            output = f"Unknown tool {call.name}. Use one of: {tool_names}."
        else:
            output = await tool.call(call.arguments, context)
        logger.info("Tool {}({}) returned {} characters", call.name, call.arguments, len(output))
        return output
