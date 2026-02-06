from dataclasses import dataclass
from typing import Type, Iterator, AsyncIterator
from langchain_core.messages import SystemMessage, HumanMessage

from ..base import BaseAgent
from ..schemas import AgentInput, AgentOutput, StreamingEvent, TextChunkEvent, AgentOutputEvent
from ..registry import AgentRegistry
from ...llms.registry import LLMRegistry

@dataclass(frozen=True, kw_only=True)
class GreetingInput(AgentInput):
    pass

@dataclass(frozen=True, kw_only=True)
class GreetingOutput(AgentOutput):
    role: str = "assistant"

@AgentRegistry.register("greeting")
class GreetingAgent(BaseAgent[GreetingInput, GreetingOutput]):
    def __init__(self, agent_id: str, **kwargs):
        super().__init__(agent_id, **kwargs)
        
        # 1. Configurable LLM
        llm_config = kwargs.get("llm_config", {"provider": "openai", "model": "gpt-4o"})
        self.llm = LLMRegistry.instantiate(
            provider=llm_config.get("provider", "openai"),
            model=llm_config.get("model", "gpt-4o")
        )
        
        # 2. Configurable Service Info
        self.service_name = kwargs.get("service_name", "datagent")
        self.service_info = kwargs.get("service_info", "data science multi-agent framework")

    @property
    def input_type(self) -> Type[GreetingInput]:
        return GreetingInput

    @property
    def output_type(self) -> Type[GreetingOutput]:
        return GreetingOutput

    async def a_run(self, input_data: GreetingInput) -> GreetingOutput:
        result = None
        async for event in self.a_stream(input_data):
            if isinstance(event, AgentOutputEvent):
                result = event.output
        
        if result:
            return result
        # Fallback
        return GreetingOutput(session_id=input_data.session_id, response="Error: No output from stream")

    def run(self, input_data: GreetingInput) -> GreetingOutput:
        import asyncio
        return asyncio.run(self.a_run(input_data))

    def stream(self, input_data: GreetingInput) -> Iterator[StreamingEvent]:
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

    async def a_stream(self, input_data: GreetingInput) -> AsyncIterator[StreamingEvent]:
        system_prompt = f"""
        You are the Greeting Agent for {self.service_name}.
        Your role is to:
        1. Warmly welcome the user ({input_data.prompt.name}).
        2. Briefly explain our service ({self.service_info}) in short sentences.
        3. Guide the user to start using the service (e.g., "You can ask me to process a dataset or generate a script.").
        
        Keep it friendly, professional, and concise.
        """
        
        messages = [
            {"role": "system", "content": system_prompt}
        ] + [
            {"role": message.role, "content": message.content} for message in input_data.history if message.role != "agent"
        ]
        
        response_text = ""
        async for chunk in self.llm.generate_chat_stream(messages):
            if chunk.content:
                response_text += chunk.content
                yield TextChunkEvent(
                    role="assistant",
                    session_id=input_data.session_id,
                    agent_name=self.name,
                    content=chunk.content
                )
        
        yield AgentOutputEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            output=GreetingOutput(
                session_id=input_data.session_id,
                content=response_text
            )
        )
