from typing import Type
from pydantic import BaseModel, Field
import aiofiles
import os
from ..base import BaseTool
from ..registry import ToolRegistry

class ReadFileInput(BaseModel):
    file_path: str = Field(..., description="The absolute path to the file to read.")
    limit: int = Field(2000, description="The number of lines to read.")
    offset: int = Field(0, description="The line number to start reading from.")

@ToolRegistry.register("read_file")
class ReadFileTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Reads a file from the local filesystem.",
            args_schema=ReadFileInput
        )

    def run(self, file_path: str, limit: int = 2000, offset: int = 0) -> str:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist."
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if offset > 0:
                    for _ in range(offset):
                        f.readline()
                
                lines = []
                for _ in range(limit):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line)
                return "".join(lines)
        except Exception as e:
            return f"Error reading file: {str(e)}"

    async def a_run(self, file_path: str, limit: int = 2000, offset: int = 0) -> str:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist."

        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                # Naive offset for async, better implementation might be needed for huge files
                # but good enough for now
                content = await f.read()
                lines = content.splitlines(keepends=True)
                return "".join(lines[offset : offset + limit])
        except Exception as e:
            return f"Error reading file: {str(e)}"
