from typing import Dict, Any
import asyncio
import subprocess
from ..base import BaseRuntime
from ..registry import RuntimeRegistry

@RuntimeRegistry.register("local_process")
class LocalRuntime(BaseRuntime):
    async def deploy(self, service_def: Dict[str, Any]) -> str:
        # For training, 'deploy' might mean starting the training script
        command = service_def.get("command", [])
        if not command:
            raise ValueError("Command is required for local runtime")
        
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return f"Started local process with PID {process.pid}"

    async def get_status(self, deployment_id: str) -> str:
        return "UNKNOWN" # simplified

    async def delete(self, deployment_id: str) -> bool:
        return True
