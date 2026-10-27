import asyncio

from pydantic import BaseModel, Field

from app.agent.tools.base import Tool, ToolContext
from app.core.database import SessionLocal
from app.models import Organization


class AddArgs(BaseModel):
    a: int = Field(description="First number")
    b: int = Field(description="Second number")


class AddTool(Tool):
    name = "add"
    description = "Add two numbers."
    args_model = AddArgs

    async def run(self, arguments: str, context: ToolContext) -> str:
        args = AddArgs.model_validate_json(arguments)
        return str(args.a + args.b)


def call_add(arguments: str) -> str:
    context = ToolContext(session=SessionLocal(), org=Organization(name="Test Store"))
    tool = AddTool()
    return asyncio.run(tool.call(arguments, context))


def test_definition_has_the_args_schema():
    tool = AddTool()
    definition = tool.definition()

    function = definition["function"]
    assert function["name"] == "add"
    assert function.get("parameters", {})["required"] == ["a", "b"]


def test_valid_arguments_run_the_tool():
    assert call_add('{"a": 2, "b": 3}') == "5"


def test_wrong_type_is_explained_to_the_model():
    result = call_add('{"a": "two", "b": 3}')

    assert result.startswith("Invalid arguments.")
    assert "a:" in result


def test_missing_argument_is_explained_to_the_model():
    assert "b: Field required" in call_add('{"a": 2}')


def test_broken_json_is_explained_to_the_model():
    assert call_add('{"a": 2,').startswith("Invalid arguments.")
