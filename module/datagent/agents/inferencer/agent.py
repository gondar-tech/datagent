from dataclasses import dataclass, field
from typing import Type, Iterator, AsyncIterator
from ...agents.base import BaseAgent
from ...agents.schemas import AgentInput, AgentOutput, StreamingEvent
from ...agents.registry import AgentRegistry

@dataclass(frozen=True, kw_only=True)
class InferencerInput(AgentInput):
    model_uri: str
    input_data: str

@dataclass(frozen=True, kw_only=True)
class InferencerOutput(AgentOutput):
    prediction: str
    latency_ms: float

@AgentRegistry.register("inferencer")
class InferencerAgent(BaseAgent[InferencerInput, InferencerOutput]):
    
    @property
    def input_type(self) -> Type[InferencerInput]:
        return InferencerInput

    @property
    def output_type(self) -> Type[InferencerOutput]:
        return InferencerOutput

    async def a_run(self, input_data: InferencerInput) -> InferencerOutput:
        # Mock inference
        return InferencerOutput(
            session_id=input_data.session_id,
            prediction="Mock Prediction",
            latency_ms=10.5
        )

    def run(self, input_data: InferencerInput) -> InferencerOutput:
        import asyncio
        return asyncio.run(self.a_run(input_data))

    def stream(self, input_data: InferencerInput) -> Iterator[StreamingEvent]:
        yield StreamingEvent(session_id=input_data.session_id, agent_name=self.name, type="prediction", data={"value": "Mock"})

    async def a_stream(self, input_data: InferencerInput) -> AsyncIterator[StreamingEvent]:
        yield StreamingEvent(session_id=input_data.session_id, agent_name=self.name, type="prediction", data={"value": "Mock"})
