from dataclasses import dataclass
from typing import Type, Iterator, AsyncIterator
from langchain_core.messages import SystemMessage, HumanMessage

from ..base import BaseAgent
from ..schemas import AgentInput, AgentOutput, StreamingEvent, TextChunkEvent, AgentOutputEvent
from ..registry import AgentRegistry
from ...llms.registry import LLMRegistry

@dataclass(frozen=True, kw_only=True)
class ExtraTopicInput(AgentInput):
    user_query: str

@dataclass(frozen=True, kw_only=True)
class ExtraTopicOutput(AgentOutput):
    response: str

@AgentRegistry.register("extra_topic")
class ExtraTopicAgent(BaseAgent[ExtraTopicInput, ExtraTopicOutput]):
    def __init__(self, agent_id: str, **kwargs):
        super().__init__(agent_id, **kwargs)
        
        # 1. Configurable LLM
        llm_config = kwargs.get("llm_config", {"provider": "openai", "model": "gpt-4o"})
        self.llm = LLMRegistry.instantiate(
            provider=llm_config.get("provider", "openai"),
            model=llm_config.get("model", "gpt-4o"),
            api_key=llm_config.get("api_key")
        )
        
        # 2. Configurable Service Info for pivoting
        self.service_info = kwargs.get("service_info", "Automated data processing, intelligent code generation, and workflow orchestration")

    @property
    def input_type(self) -> Type[ExtraTopicInput]:
        return ExtraTopicInput

    @property
    def output_type(self) -> Type[ExtraTopicOutput]:
        return ExtraTopicOutput

    async def a_run(self, input_data: ExtraTopicInput) -> ExtraTopicOutput:
        result = None
        async for event in self.a_stream(input_data):
            if isinstance(event, AgentOutputEvent):
                result = event.output
        
        if result:
            return result
        # Fallback if stream didn't yield output (should not happen if implemented correctly)
        return ExtraTopicOutput(session_id=input_data.session_id, response="Error: No output from stream")

    def run(self, input_data: ExtraTopicInput) -> ExtraTopicOutput:
        import asyncio
        return asyncio.run(self.a_run(input_data))

    def stream(self, input_data: ExtraTopicInput) -> Iterator[StreamingEvent]:
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

    async def a_stream(self, input_data: ExtraTopicInput) -> AsyncIterator[StreamingEvent]:
        system_prompt = f"""
        You are a helpful assistant for the Avaloka Datagent service.
        The user has asked a question that is NOT directly related to our core service.
        
        Your goal is to:
        1. Answer the user's question helpfully and politely.
        2. Gently pivot back to explaining the pros of our Datagent service.
        3. Guide them to use our service.
        
        Our Service Highlights:
        {self.service_info}
        
        Keep the response concise but friendly.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=input_data.user_query)
        ]
        
        response_text = ""
        async for chunk in self.llm.generate_stream(messages):
            if chunk.content:
                response_text += chunk.content
                yield TextChunkEvent(
                    session_id=input_data.session_id,
                    agent_name=self.name,
                    content=chunk.content
                )
        
        yield AgentOutputEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            output=ExtraTopicOutput(
                session_id=input_data.session_id,
                response=response_text
            )
        )
