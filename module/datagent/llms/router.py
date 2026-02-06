from typing import List, Dict, Any, Optional
from .base import BaseLLM, LLMResponse
from .registry import LLMRegistry

class LLMRouter:
    def __init__(self, default_provider: str = "openai", default_model: str = "gpt-4-turbo"):
        self.default_provider = default_provider
        self.default_model = default_model
        self.providers: Dict[str, BaseLLM] = {}

    def get_llm(self, provider: Optional[str] = None, model: Optional[str] = None) -> BaseLLM:
        provider = provider or self.default_provider
        model = model or self.default_model
        
        key = f"{provider}:{model}"
        if key not in self.providers:
            self.providers[key] = LLMRegistry.create(provider, model=model)
        
        return self.providers[key]

    async def route_request(self, messages: List[Dict[str, str]], provider: Optional[str] = None, **kwargs) -> LLMResponse:
        llm = self.get_llm(provider)
        return await llm.generate_chat(messages, **kwargs)
