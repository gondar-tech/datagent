from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Iterator, AsyncIterator
from .schemas import AgentInput, AgentOutput, StreamingEvent

In = TypeVar("In", bound=AgentInput)
Out = TypeVar("Out", bound=AgentOutput)

class BaseAgent(ABC, Generic[In, Out]):
    def __init__(self, name: str):
        self.name = name

    @property
    @abstractmethod
    def input_type(self) -> Type[In]:
        pass

    @property
    @abstractmethod
    def output_type(self) -> Type[Out]:
        pass

    @abstractmethod
    async def a_run(self, input_data: In) -> Out:
        pass

    def run(self, input_data: In) -> Out:
        raise NotImplementedError("Sync run not implemented")

    def stream(self, input_data: In) -> Iterator[StreamingEvent]:
        raise NotImplementedError("Stream not implemented")

    async def a_stream(self, input_data: In) -> AsyncIterator[StreamingEvent]:
        raise NotImplementedError("Async stream not implemented")
