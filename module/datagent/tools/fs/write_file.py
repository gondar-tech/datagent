from typing import Type
from pydantic import BaseModel, Field
import aiofiles
import os
from ..base import BaseTool
from ..registry import ToolRegistry

class WriteFileInput(BaseModel):
    file_path: str = Field(..., description="The absolute path to the file to write.")
    content: str = Field(..., description="The content to write to the file.")

@ToolRegistry.register("write_file")
class WriteFileTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Writes content to a file. Overwrites if exists.",
            args_schema=WriteFileInput
        )

    def run(self, file_path: str, content: str) -> str:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    async def a_run(self, file_path: str, content: str) -> str:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
