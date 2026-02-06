from dataclasses import dataclass
from typing import Type, Iterator, AsyncIterator
from ..base import BaseAgent
from ..schemas import AgentInput, AgentOutput, StreamingEvent, TextChunkEvent
from ..registry import AgentRegistry

@dataclass(frozen=True, kw_only=True)
class PlannerInput(AgentInput):
    user_request: str

@dataclass(frozen=True, kw_only=True)
class PlannerOutput(AgentOutput):
    plan: str

@AgentRegistry.register("planner")
class PlannerAgent(BaseAgent[PlannerInput, PlannerOutput]):
    @property
    def input_type(self) -> Type[PlannerInput]:
        return PlannerInput

    @property
    def output_type(self) -> Type[PlannerOutput]:
        return PlannerOutput

    async def a_run(self, input_data: PlannerInput) -> PlannerOutput:
        return PlannerOutput(
            session_id=input_data.session_id,
            plan=f"Plan for: {input_data.user_request}"
        )

    async def a_stream(self, input_data: PlannerInput) -> AsyncIterator[StreamingEvent]:
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            content=f"Received request: {input_data.user_request}\n"
        )
        
        # Simulate LLM thinking
        steps = ["Decomposing task", "Identifying resources", "Drafting plan"]
        for i, step in enumerate(steps):
            yield TextChunkEvent(
                session_id=input_data.session_id,
                agent_name=self.name,
                content=f"Step {i+1}: {step}...\n"
            )
            # In real world, await asyncio.sleep or await LLM stream
            
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            content="Plan created successfully.\n"
        )
