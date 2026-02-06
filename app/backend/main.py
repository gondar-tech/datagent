from fastapi import FastAPI
from .routers import workflow, health
from datagent.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Avaloka AI Datagent API"
)

app.include_router(health.router)
app.include_router(workflow.router, prefix="/api/v1/workflow", tags=["workflow"])

@app.get("/")
async def root():
    return {"message": "Welcome to Avaloka AI Datagent API"}
