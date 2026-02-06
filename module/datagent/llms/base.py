from typing import Any, Dict, List, Optional, AsyncIterator
from abc import ABC, abstractmethod
from pydantic import BaseModel

class LLMResponse(BaseModel):
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    usage: Optional[Dict[str, int]] = None

class StreamingChunk(BaseModel):
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    finish_reason: Optional[str] = None

class BaseLLM(ABC):
    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs):
        self.model = model
        self.api_key = api_key
        self.kwargs = kwargs

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        pass
    
    @abstractmethod
    async def generate_chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        pass

    @abstractmethod
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[StreamingChunk]:
        pass

    @abstractmethod
    async def generate_chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[StreamingChunk]:
        pass
