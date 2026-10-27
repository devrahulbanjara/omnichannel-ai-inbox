from dataclasses import dataclass

from openai.types.chat import ChatCompletionToolParam
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization


@dataclass
class ToolContext:
    """Who a tool acts for. Set by the server, never by the model."""

    session: AsyncSession
    org: Organization


class Tool:
    """A function the model can ask to run.

    The Args model is used twice: its JSON schema tells the model what to send,
    and run() validates what the model actually sent with it.
    """

    name: str
    description: str  # the model reads this to decide when to use the tool
    args_model: type[BaseModel]

    def definition(self) -> ChatCompletionToolParam:
        """The tool as the model sees it."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_model.model_json_schema(),
            },
        }

    async def call(self, arguments: str, context: ToolContext) -> str:
        """Run the tool. Invalid arguments are returned as text, so the model can correct
        its call instead of the turn crashing."""
        try:
            return await self.run(arguments, context)
        except ValidationError as exc:
            return self.explain_invalid_arguments(exc)

    async def run(self, arguments: str, context: ToolContext) -> str:
        """The tool's work. Starts with `args = MyArgs.model_validate_json(arguments)`.
        Returns short text for the model to read."""
        raise NotImplementedError

    @staticmethod
    def explain_invalid_arguments(exc: ValidationError) -> str:
        problems = []
        for error in exc.errors():
            parts = []
            for part in error["loc"]:  # e.g. ("filters", "max_price") -> "filters.max_price"
                parts.append(str(part))
            field = ".".join(parts) or "arguments"
            problems.append(f"{field}: {error['msg']}")
        all_problems = "; ".join(problems)
        return f"Invalid arguments. {all_problems}"
