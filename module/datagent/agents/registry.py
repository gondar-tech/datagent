from typing import Dict, Type, Any
from .base import BaseAgent

class AgentRegistry:
    _registry: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(agent_cls: Type[BaseAgent]):
            cls._registry[name] = agent_cls
            return agent_cls
        return decorator

    @classmethod
    def instantiate(cls, agent_type: str, **kwargs) -> BaseAgent:
        if agent_type not in cls._registry:
            raise ValueError(f"Agent type {agent_type} not found")
        return cls._registry[agent_type](**kwargs)
