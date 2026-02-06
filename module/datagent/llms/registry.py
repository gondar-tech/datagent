from typing import Dict, Type
from .base import BaseLLM

class LLMRegistry:
    _registry: Dict[str, Type[BaseLLM]] = {}

    @classmethod
    def register(cls, provider_name: str):
        def decorator(llm_cls: Type[BaseLLM]):
            cls._registry[provider_name] = llm_cls
            return llm_cls
        return decorator

    @classmethod
    def instantiate(cls, provider: str, **kwargs) -> BaseLLM:
        if provider not in cls._registry:
            raise ValueError(f"LLM provider {provider} not found")
        return cls._registry[provider](**kwargs)
