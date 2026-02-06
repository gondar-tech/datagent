from typing import List, Dict, Any, Optional, AsyncIterator
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage

from ..base import BaseLLM, LLMResponse, StreamingChunk
from ..registry import LLMRegistry
from ...settings import settings

@LLMRegistry.register("groq")
class GroqLLM(BaseLLM):
    def __init__(self, model: str = "llama-3.3-70b-versatile", api_key: Optional[str] = settings.GROQ_API_KEY, **kwargs):
        super().__init__(model, api_key, **kwargs)
        self.client = ChatGroq(
            model_name=model,
            api_key=self.api_key,
            streaming=True,
            **kwargs
        )

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        lc_messages = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content") or ""
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))
        return lc_messages

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        return await self.generate_chat([{"role": "user", "content": prompt}], **kwargs)

    async def generate_chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        response = await self.client.ainvoke(messages, **kwargs)
        
        usage = response.response_metadata.get("token_usage")
        tool_calls = None
        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_calls = response.tool_calls
            
        return LLMResponse(
            content=str(response.content),
            tool_calls=tool_calls,
            usage=usage
        )

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[StreamingChunk]:
        async for chunk in self.generate_chat_stream([{"role": "user", "content": prompt}], **kwargs):
            yield chunk

    async def generate_chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[StreamingChunk]:
        lc_messages = self._convert_messages(messages)
        async for chunk in self.client.astream(lc_messages, **kwargs):
            content = str(chunk.content) if chunk.content else None
            
            tool_calls = None
            if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
                tool_calls = [tc if isinstance(tc, dict) else tc.__dict__ for tc in chunk.tool_call_chunks]

            yield StreamingChunk(
                content=content,
                tool_calls=tool_calls,
                finish_reason=chunk.response_metadata.get("finish_reason") if hasattr(chunk, "response_metadata") else None
            )
