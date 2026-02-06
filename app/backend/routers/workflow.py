from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import asyncio
import uuid
import os
from datetime import datetime

from datagent.bootstrap import bootstrap_app
from datagent.core.workflow_executor import WorkflowExecutor
from datagent.core.yaml_workflow_loader import YamlWorkflowLoader
from datagent.core.storage import SessionStorage
from datagent.agents.schemas import BasePrompt, FileData

router = APIRouter()

# Ensure app is bootstrapped
bootstrap_app()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {
        "filename": file.filename,
        "url": os.path.abspath(file_path),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/stream")
async def stream_workflow(
    prompt: str = Form(...),
    session_id: Optional[str] = Form(None),
    files: Optional[str] = Form(None)  # JSON string of file metadata
):
    # 1. Handle Session ID
    if not session_id:
        session_id = f"web-session-{uuid.uuid4()}"
    
    # 2. Process Files
    processed_files = []
    if files:
        try:
            files_data = json.loads(files)
            for f in files_data:
                processed_files.append(FileData(
                    filename=f.get("filename"),
                    url=f.get("url"),
                    timestamp=datetime.fromisoformat(f.get("timestamp")) if f.get("timestamp") else datetime.utcnow()
                ))
        except json.JSONDecodeError:
            # Fallback or ignore if invalid JSON
            pass

    # 3. Load Workflow
    # In a real app, we might cache this or load dynamically based on request
    loader = YamlWorkflowLoader()
    try:
        workflow_def = loader.load("workflows/workflow.yaml")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load workflow: {str(e)}")

    # 4. Load Context
    session_storage = SessionStorage()
    current_context = session_storage.load_context(session_id)

    # 5. Prepare Execution
    executor = WorkflowExecutor(workflow_def)
    base_prompt = BasePrompt(
        name="Web User",
        email="web@datagent.ai",
        query=prompt,
        files=processed_files
    )

    async def event_generator():
        try:
            async for event in executor.run_stream(base_prompt, current_context):
                # Convert dataclass to dict for JSON serialization
                # We need to handle datetime serialization if present in event.data
                
                # Simple serialization helper
                def json_serial(obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    return str(obj)

                # Extract relevant data based on event type
                payload = {
                    "type": event.type,
                    "node_id": getattr(event, "node_id", None),
                    "agent_name": getattr(event, "agent_name", None),
                    "role": getattr(event, "role", "assistant"),
                    "content": getattr(event, "content", None),
                    "data": getattr(event, "data", {})
                }
                
                yield f"data: {json.dumps(payload, default=json_serial)}\n\n"
                
                # Save context on update
                if event.type == "context_update":
                    session_storage.save_context(event.context)

            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_payload = {"type": "error", "content": str(e)}
            yield f"data: {json.dumps(error_payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
