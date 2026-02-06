from fastapi import FastAPI
from .routers import workflow, health
from datagent.settings import settings

app = FastAPI(
    title="Avaloka AI",
    version="0.1.0",
    description="Data sciece agent system"
)

app.include_router(health.router)
app.include_router(workflow.router, prefix="/api/v1/workflow", tags=["workflow"])

@app.get("/")
async def root():
    return {"message": "Welcome to Avaloka AI Datagent API"}
