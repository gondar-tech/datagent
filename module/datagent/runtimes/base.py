from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseRuntime(ABC):
    @abstractmethod
    async def submit_job(self, job_spec: Dict[str, Any]) -> str:
        """Submits a job and returns a job ID."""
        pass

    @abstractmethod
    async def get_status(self, job_id: str) -> str:
        """Returns the status of the job."""
        pass

    @abstractmethod
    async def get_logs(self, job_id: str) -> str:
        """Returns logs for the job."""
        pass
