from typing import Any, Dict, Optional, Type, Union
from abc import ABC, abstractmethod
from pydantic import BaseModel

class BaseTool(ABC):
    name: str
    description: str
    args_schema: Optional[Type[BaseModel]] = None

    def __init__(self, name: str, description: str, args_schema: Optional[Type[BaseModel]] = None):
        self.name = name
        self.description = description
        self.args_schema = args_schema

    @abstractmethod
    def run(self, **kwargs) -> Any:
        pass

    @abstractmethod
    async def a_run(self, **kwargs) -> Any:
        pass

    def to_openai_schema(self) -> Dict[str, Any]:
        """Converts the tool to an OpenAI function schema."""
        parameters = {}
        if self.args_schema:
            parameters = self.args_schema.model_json_schema()
            # Clean up schema for OpenAI compatibility if needed
            if "title" in parameters:
                del parameters["title"]
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": parameters
            }
        }
