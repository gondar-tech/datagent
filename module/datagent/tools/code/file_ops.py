from typing import Any
from pydantic import BaseModel, Field
from ..base import BaseTool
from ..registry import ToolRegistry
import os

class WriteFileInput(BaseModel):
    file_path: str = Field(..., description="Absolute path to the file")
    content: str = Field(..., description="Content to write")

@ToolRegistry.register("write_file")
class WriteFileTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Writes content to a file",
            args_schema=WriteFileInput
        )

    def run(self, file_path: str, content: str) -> str:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File written to {file_path}"

    async def a_run(self, file_path: str, content: str) -> str:
        return self.run(file_path, content)
