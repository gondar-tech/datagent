from dataclasses import dataclass, field
from typing import Type, Iterator, AsyncIterator, List, Optional
from ...agents.base import BaseAgent
from ...agents.schemas import AgentInput, AgentOutput, StreamingEvent, TextChunkEvent
from ...agents.registry import AgentRegistry
from ...runtimes.training.ray_runtime import RayRuntime

@dataclass(frozen=True, kw_only=True)
class TrainerInput(AgentInput):
    model_config: str
    dataset_path: str
    epochs: int = 1
    compute_config: Optional[str] = None

@dataclass(frozen=True, kw_only=True)
class TrainerOutput(AgentOutput):
    job_id: str
    status: str
    metrics: dict = field(default_factory=dict)

@AgentRegistry.register("trainer")
class TrainerAgent(BaseAgent[TrainerInput, TrainerOutput]):
    
    def __init__(self, name: str = "trainer"):
        super().__init__(name)
        self.runtime = RayRuntime()

    @property
    def input_type(self) -> Type[TrainerInput]:
        return TrainerInput

    @property
    def output_type(self) -> Type[TrainerOutput]:
        return TrainerOutput

    async def a_run(self, input_data: TrainerInput) -> TrainerOutput:
        # Submit job to Ray
        job_id = await self.runtime.submit_job({
            "entrypoint": f"python train.py --config {input_data.model_config} --data {input_data.dataset_path}",
            "runtime_env": {"pip": ["torch", "transformers"]}
        })
        
        return TrainerOutput(
            session_id=input_data.session_id,
            job_id=job_id,
            status="submitted",
            metrics={"epochs": input_data.epochs}
        )

    def run(self, input_data: TrainerInput) -> TrainerOutput:
        import asyncio
        return asyncio.run(self.a_run(input_data))

    def stream(self, input_data: TrainerInput) -> Iterator[StreamingEvent]:
        yield TextChunkEvent(session_id=input_data.session_id, agent_name=self.name, chunk_index=0, content="Submitting training job...")

    async def a_stream(self, input_data: TrainerInput) -> AsyncIterator[StreamingEvent]:
        yield TextChunkEvent(session_id=input_data.session_id, agent_name=self.name, chunk_index=0, content="Submitting training job...")
