from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class WorkflowRequest(BaseModel):
    workflow_path: str
    inputs: Dict[str, Any]

@router.post("/run")
async def run_workflow(request: WorkflowRequest):
    # This would invoke the WorkflowExecutor
    return {"status": "running", "workflow": request.workflow_path}
