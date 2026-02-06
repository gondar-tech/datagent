from typing import Type, List, Optional
from pydantic import BaseModel, Field
import subprocess
import asyncio
from ..base import BaseTool
from ..registry import ToolRegistry

class ShellCommandInput(BaseModel):
    command: str = Field(..., description="The shell command to execute.")
    cwd: Optional[str] = Field(None, description="The directory to execute the command in.")

@ToolRegistry.register("shell_command")
class ShellCommandTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="shell_command",
            description="Executes a shell command.",
            args_schema=ShellCommandInput
        )

    def run(self, command: str, cwd: Optional[str] = None) -> str:
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=cwd
            )
            return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        except Exception as e:
            return f"Error executing command: {str(e)}"

    async def a_run(self, command: str, cwd: Optional[str] = None) -> str:
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            stdout, stderr = await process.communicate()
            return f"STDOUT:\n{stdout.decode()}\nSTDERR:\n{stderr.decode()}"
        except Exception as e:
            return f"Error executing command: {str(e)}"
