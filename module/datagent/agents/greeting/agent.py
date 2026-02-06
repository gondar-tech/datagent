from dataclasses import dataclass
from typing import Type
from ..base import BaseAgent
from ..schemas import AgentInput, AgentOutput
from ..registry import AgentRegistry

@dataclass(frozen=True, kw_only=True)
class GreetingInput(AgentInput):
    name: str

@dataclass(frozen=True, kw_only=True)
class GreetingOutput(AgentOutput):
    greeting: str

@AgentRegistry.register("greeting")
class GreetingAgent(BaseAgent[GreetingInput, GreetingOutput]):
    @property
    def input_type(self) -> Type[GreetingInput]:
        return GreetingInput

    @property
    def output_type(self) -> Type[GreetingOutput]:
        return GreetingOutput

    async def a_run(self, input_data: GreetingInput) -> GreetingOutput:
        return GreetingOutput(
            session_id=input_data.session_id,
            greeting=f"Hello, {input_data.name}!"
        )
