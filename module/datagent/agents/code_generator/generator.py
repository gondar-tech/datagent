from dataclasses import dataclass, field
from typing import Type, Iterator, AsyncIterator, Dict
from ...agents.base import BaseAgent
from ...agents.schemas import AgentInput, AgentOutput, StreamingEvent, TextChunkEvent
from ...agents.registry import AgentRegistry
from .multi_file_builder import MultiFileBuilder

@dataclass(frozen=True, kw_only=True)
class CodeGeneratorInput(AgentInput):
    requirements: str
    context_files: str = ""

@dataclass(frozen=True, kw_only=True)
class CodeGeneratorOutput(AgentOutput):
    generated_files: Dict[str, str] = field(default_factory=dict)
    summary: str = ""

@AgentRegistry.register("code_generator")
class CodeGeneratorAgent(BaseAgent[CodeGeneratorInput, CodeGeneratorOutput]):
    
    def __init__(self, name: str = "code_generator"):
        super().__init__(name)
        self.builder = MultiFileBuilder()

    @property
    def input_type(self) -> Type[CodeGeneratorInput]:
        return CodeGeneratorInput

    @property
    def output_type(self) -> Type[CodeGeneratorOutput]:
        return CodeGeneratorOutput

    async def a_run(self, input_data: CodeGeneratorInput) -> CodeGeneratorOutput:
        # Simulate generating multiple files
        files = {
            "main.py": "print('Hello Generated World')",
            "utils.py": "def helper(): pass"
        }
        
        # In a real scenario, we might write them to a temp dir or just return them
        # self.builder.build(files) # Optional: Write to disk
        
        return CodeGeneratorOutput(
            session_id=input_data.session_id,
            generated_files=files,
            summary="Generated 2 files."
        )

    def run(self, input_data: CodeGeneratorInput) -> CodeGeneratorOutput:
        import asyncio
        return asyncio.run(self.a_run(input_data))

    def stream(self, input_data: CodeGeneratorInput) -> Iterator[StreamingEvent]:
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            chunk_index=0,
            content="Generating main.py..."
        )

    async def a_stream(self, input_data: CodeGeneratorInput) -> AsyncIterator[StreamingEvent]:
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            chunk_index=0,
            content="Generating main.py..."
        )
