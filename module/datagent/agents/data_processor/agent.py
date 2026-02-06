from dataclasses import dataclass
from typing import Type, Iterator, AsyncIterator
from langchain_core.messages import SystemMessage, HumanMessage

from ..base import BaseAgent
from ..schemas import AgentInput, AgentOutput, StreamingEvent, TextChunkEvent, AgentOutputEvent
from ..registry import AgentRegistry

@dataclass(frozen=True, kw_only=True)
class DataProcessingInput(AgentInput):
    user_request: str

@dataclass(frozen=True, kw_only=True)
class DataProcessingOutput(AgentOutput):
    result: str

@AgentRegistry.register("data_processor")
class DataProcessingAgent(BaseAgent[DataProcessingInput, DataProcessingOutput]):
    def __init__(self, agent_id: str, **kwargs):
        super().__init__(agent_id, **kwargs)
        # In future, we can accept tools/config here
    
    @property
    def input_type(self) -> Type[DataProcessingInput]:
        return DataProcessingInput

    @property
    def output_type(self) -> Type[DataProcessingOutput]:
        return DataProcessingOutput

    async def a_run(self, input_data: DataProcessingInput) -> DataProcessingOutput:
        result = None
        async for event in self.a_stream(input_data):
            if isinstance(event, AgentOutputEvent):
                result = event.output
        if result:
            return result
        return DataProcessingOutput(
            session_id=input_data.session_id,
            result=f"Processed request: {input_data.user_request}"
        )

    def run(self, input_data: DataProcessingInput) -> DataProcessingOutput:
        import asyncio
        return asyncio.run(self.a_run(input_data))

    def stream(self, input_data: DataProcessingInput) -> Iterator[StreamingEvent]:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        agen = self.a_stream(input_data)
        try:
            while True:
                try:
                    yield loop.run_until_complete(agen.__anext__())
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

    async def a_stream(self, input_data: DataProcessingInput) -> AsyncIterator[StreamingEvent]:
        # For now, this is a placeholder that just acknowledges the request
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            content=f"[Data Processing Agent] I have received your request: '{input_data.user_request}'.\n"
        )
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            content="Simulating data processing task...\n"
        )
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            content="Task completed successfully.\n"
        )
        
        yield AgentOutputEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            output=DataProcessingOutput(
                session_id=input_data.session_id,
                result=f"Processed request: {input_data.user_request}"
            )
        )
