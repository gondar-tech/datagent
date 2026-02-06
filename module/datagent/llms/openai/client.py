from typing import List, Dict, Any, Optional, AsyncIterator
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_core.outputs import ChatGenerationChunk

from ..base import BaseLLM, LLMResponse, StreamingChunk
from ..registry import LLMRegistry
from ...settings import settings

@LLMRegistry.register("openai")
class OpenAILLM(BaseLLM):
    def __init__(self, model: str = "gpt-4-turbo", api_key: Optional[str] = settings.OPENAI_API_KEY, **kwargs):
        super().__init__(model, api_key, **kwargs)
        self.client = ChatOpenAI(
            model=model,
            api_key=self.api_key,
            streaming=True,
            **kwargs
        )

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        lc_messages = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                # Default to human for unknown roles or handle error
                lc_messages.append(HumanMessage(content=content))
        return lc_messages

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        return await self.generate_chat([{"role": "user", "content": prompt}], **kwargs)

    async def generate_chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        lc_messages = self._convert_messages(messages)
        # LangChain's ainvoke returns an AIMessage
        response = await self.client.ainvoke(lc_messages, **kwargs)
        
        # Extract usage if available (LangChain often puts it in response_metadata)
        usage = response.response_metadata.get("token_usage")
        
        # Handle tool calls if any (LangChain standardizes this in newer versions)
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
            
            # Map tool call chunks if present
            tool_calls = None
            if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
                # LangChain's tool_call_chunks are objects, we might need to serialize them or pass as dicts
                # For now, let's keep it simple or convert if BaseLLM expects dicts
                tool_calls = [tc if isinstance(tc, dict) else tc.__dict__ for tc in chunk.tool_call_chunks]

            yield StreamingChunk(
                content=content,
                tool_calls=tool_calls,
                finish_reason=chunk.response_metadata.get("finish_reason") if hasattr(chunk, "response_metadata") else None
            )
