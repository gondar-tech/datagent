from typing import Type, List
from pydantic import BaseModel, Field
import os
from ..base import BaseTool
from ..registry import ToolRegistry
import glob

class ListDirInput(BaseModel):
    path: str = Field(..., description="The directory path to list.")

@ToolRegistry.register("list_dir")
class ListDirTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="list_dir",
            description="Lists files and directories in a given path.",
            args_schema=ListDirInput
        )

    def run(self, path: str) -> str:
        try:
            if not os.path.exists(path):
                return f"Error: Path {path} does not exist."
            
            items = os.listdir(path)
            # Add type indicator
            result = []
            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    result.append(f"{item}/")
                else:
                    result.append(item)
            return "\n".join(result)
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    async def a_run(self, path: str) -> str:
        # os.listdir is fast enough for sync usually, but we can wrap if strictly needed
        return self.run(path)
