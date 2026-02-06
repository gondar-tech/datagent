from dataclasses import dataclass
from typing import Type
from ..base import BaseAgent
from ..schemas import AgentInput, AgentOutput
from ..registry import AgentRegistry

@dataclass(frozen=True, kw_only=True)
class DataProcessorInput(AgentInput):
    dataset_uri: str

@dataclass(frozen=True, kw_only=True)
class DataProcessorOutput(AgentOutput):
    processed_uri: str

@AgentRegistry.register("data_processor")
class DataProcessorAgent(BaseAgent[DataProcessorInput, DataProcessorOutput]):
    @property
    def input_type(self) -> Type[DataProcessorInput]:
        return DataProcessorInput

    @property
    def output_type(self) -> Type[DataProcessorOutput]:
        return DataProcessorOutput

    async def a_run(self, input_data: DataProcessorInput) -> DataProcessorOutput:
        return DataProcessorOutput(
            session_id=input_data.session_id,
            processed_uri=f"{input_data.dataset_uri}_processed"
        )
