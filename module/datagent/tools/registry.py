from typing import Dict, Type, Any, Optional
from .base import BaseTool

class ToolRegistry:
    _registry: Dict[str, Type[BaseTool]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(tool_cls: Type[BaseTool]):
            cls._registry[name] = tool_cls
            return tool_cls
        return decorator

    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseTool]]:
        return cls._registry.get(name)

    @classmethod
    def instantiate(cls, name: str, **kwargs) -> BaseTool:
        tool_cls = cls.get(name)
        if not tool_cls:
            raise ValueError(f"Tool {name} not found")
        return tool_cls(**kwargs)

    @classmethod
    def list_tools(cls) -> Dict[str, str]:
        return {name: tool.description for name, tool in cls._registry.items() if hasattr(tool, 'description')}
