from dataclasses import dataclass
from typing import Type, Iterator, AsyncIterator

from ..base import BaseAgent
from ..schemas import AgentInput, AgentOutput, StreamingEvent, TextChunkEvent, ContextUpdateEvent, AgentOutputEvent
from ..registry import AgentRegistry
from ...llms.registry import LLMRegistry

@dataclass(frozen=True, kw_only=True)
class PlannerInput(AgentInput):
    pass

@dataclass(frozen=True, kw_only=True)
class PlannerOutput(AgentOutput):
    next_action: str
    reasoning: str

@AgentRegistry.register("planner")
class PlannerAgent(BaseAgent[PlannerInput, PlannerOutput]):
    def __init__(self, agent_id: str, **kwargs):
        super().__init__(agent_id, **kwargs)
        
        # Configurable LLM
        llm_config = kwargs.get("llm_config", {"provider": "openai", "model": "gpt-4o"})
        self.llm = LLMRegistry.instantiate(
            provider=llm_config.get("provider", "openai"),
            model=llm_config.get("model", "gpt-4o")
        )

    @property
    def input_type(self) -> Type[PlannerInput]:
        return PlannerInput

    @property
    def output_type(self) -> Type[PlannerOutput]:
        return PlannerOutput

    async def a_run(self, input_data: PlannerInput) -> PlannerOutput:
        # For non-streaming, we can just consume the stream
        result = None
        async for event in self.a_stream(input_data):
            if isinstance(event, AgentOutputEvent):
                result = event.output
        
        if result:
            return result
            
        return PlannerOutput(session_id=input_data.session_id, next_action="unknown", reasoning="Failed to get output from stream")

    def run(self, input_data: PlannerInput) -> PlannerOutput:
        import asyncio
        return asyncio.run(self.a_run(input_data))

    def stream(self, input_data: PlannerInput) -> Iterator[StreamingEvent]:
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

    async def a_stream(self, input_data: PlannerInput) -> AsyncIterator[StreamingEvent]:
        system_prompt = """
        You are the Planner Agent for Avaloka Datagent.
        Your task is to analyze the user's input and decide the next best action (agent to call).

        Available Actions (Agents):
        1. 'greeting': 
           - Use when the user says "hi", "hello", "good morning", etc.
           - Use for casual pleasantries unrelated to work tasks.
        
        2. 'data_processor':
           - Use when the user asks to process data, clean files, analyze datasets, or mentions specific file URLs/paths for processing.
           - Use when the user explicitly wants to perform a data-related task.
           
        3. 'extra_topic':
           - Use when the user asks something completely unrelated to our service (e.g., "What is the capital of France?", "How to cook pasta?").
           - Use when the request is out of scope for data/code tasks.

        Instructions:
        - Analyze the user request.
        - Output your reasoning briefly.
        - Finally, output the selected action keyword on a new line starting with "ACTION: ".
        
        Example 1:
        User: "Hi there!"
        Response:
        User is greeting.
        ACTION: greeting
        
        Example 2:
        User: "Please clean this csv file."
        Response:
        User wants data processing.
        ACTION: data_processor
        
        Example 3:
        User: "Who won the super bowl?"
        Response:
        User is asking general knowledge question unrelated to service.
        ACTION: extra_topic
        """
        
        messages = [
            {"role": "system", "content": system_prompt}
        ] + [
            {"role": message.role, "content": message.content} for message in input_data.history if message.role != "agent"
        ]
        
        full_response = ""
        async for chunk in self.llm.generate_chat_stream(messages):
            if chunk.content:
                full_response += chunk.content
                
        # Parse the decision
        next_action = "extra_topic" # Default fallback
        for line in full_response.split('\n'):
            if line.strip().startswith("ACTION:"):
                next_action = line.strip().replace("ACTION:", "").strip().lower()
        
        # Emit final output event
        yield AgentOutputEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            output=PlannerOutput(
                session_id=input_data.session_id,
                next_action=next_action,
                reasoning=full_response
            )
        )
