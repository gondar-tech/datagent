from typing import Dict, Any
import subprocess
from ..base import BaseRuntime
from ..registry import RuntimeRegistry

@RuntimeRegistry.register("fastapi")
class FastAPIRuntime(BaseRuntime):
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.process = None

    async def deploy(self, service_def: Dict[str, Any]) -> str:
        # Mock starting a FastAPI app
        return f"Started FastAPI service {service_def.get('name')} on {self.host}:{self.port}"

    async def get_status(self, deployment_id: str) -> str:
        return "RUNNING" if self.process else "STOPPED"

    async def delete(self, deployment_id: str) -> bool:
        if self.process:
            self.process.terminate()
        return True
