from dataclasses import dataclass
from typing import Type, Iterator, AsyncIterator
from ..base import BaseAgent
from ..schemas import AgentInput, AgentOutput, StreamingEvent, TextChunkEvent
from ..registry import AgentRegistry

@dataclass(frozen=True, kw_only=True)
class OrchestratorInput(AgentInput):
    workflow_id: str

@dataclass(frozen=True, kw_only=True)
class OrchestratorOutput(AgentOutput):
    status: str

@AgentRegistry.register("orchestrator")
class OrchestratorAgent(BaseAgent[OrchestratorInput, OrchestratorOutput]):
    @property
    def input_type(self) -> Type[OrchestratorInput]:
        return OrchestratorInput

    @property
    def output_type(self) -> Type[OrchestratorOutput]:
        return OrchestratorOutput

    async def a_run(self, input_data: OrchestratorInput) -> OrchestratorOutput:
        # For non-streaming run, we assume it just finishes
        return OrchestratorOutput(
            session_id=input_data.session_id,
            status="Orchestrated"
        )

    async def a_stream(self, input_data: OrchestratorInput) -> AsyncIterator[StreamingEvent]:
        # Simulate thinking/planning
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            content="Analyzing workflow requirements...\n"
        )
        import asyncio
        await asyncio.sleep(0.5)
        
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            content=f"Preparing to execute workflow: {input_data.workflow_id}\n"
        )
        
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            content="Plan verified. Starting execution.\n"
        )
