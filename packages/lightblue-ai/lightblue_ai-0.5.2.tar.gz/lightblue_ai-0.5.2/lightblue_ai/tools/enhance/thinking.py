from typing import Annotated

from pydantic import Field

from lightblue_ai.tools.base import LightBlueTool, Scope
from lightblue_ai.tools.extensions import hookimpl


class ThinkingTool(LightBlueTool):
    """https://www.anthropic.com/engineering/claude-think-tool"""

    def __init__(self):
        self.name = "thinking"
        self.scopes = [Scope.read]
        self.description = "Use the tool to think about something. It will not obtain new information or change the database, but just append the thought to the log. Use it when complex reasoning or some cache memory is needed."

    async def call(
        self,
        thought: Annotated[str, Field(description="A thought to think about.")],
    ) -> dict[str, str]:
        return {
            "thought": thought,
        }


@hookimpl
def register(manager):
    manager.register(ThinkingTool())
