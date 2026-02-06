from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Iterator, AsyncIterator
from .schemas import AgentInput, AgentOutput, StreamingEvent

In = TypeVar("In", bound=AgentInput)
Out = TypeVar("Out", bound=AgentOutput)

class BaseAgent(ABC, Generic[In, Out]):
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.config = kwargs

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

    @abstractmethod
    def run(self, input_data: In) -> Out:
        pass

    @abstractmethod
    def stream(self, input_data: In) -> Iterator[StreamingEvent]:
        pass

    @abstractmethod
    async def a_stream(self, input_data: In) -> AsyncIterator[StreamingEvent]:
        pass
