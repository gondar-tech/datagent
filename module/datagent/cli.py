from ast import Return
import typer
import asyncio
import uuid
from typing import Optional
from datagent.settings import settings
from datagent.bootstrap import bootstrap_app
from datagent.core.workflow_executor import WorkflowExecutor
from datagent.core.yaml_workflow_loader import YamlWorkflowLoader
from datagent.core.storage import SessionStorage

app = typer.Typer()

@app.command()
def info():
    """Display application information."""
    typer.echo(f"Env: {settings.ENV}")
    typer.echo(f"Debug: {settings.DEBUG}")

@app.command()
def run_workflow(
    workflow_path: str = typer.Argument(..., help="Path to workflow YAML file"),
    input_text: str = typer.Option(..., "--input", "-i", help="Initial user input"),
    session_id: Optional[str] = typer.Option(None, "--session-id", "-s", help="Session ID"),
    stream: bool = typer.Option(True, "--stream/--no-stream", help="Stream output tokens")
):
    """Run a workflow from a YAML file."""
    bootstrap_app()
    
    loader = YamlWorkflowLoader()
    try:
        wf = loader.load(workflow_path)
    except Exception as e:
        typer.echo(f"Error loading workflow: {e}", err=True)
        Return

    if not session_id:
        session_id = f"cli-run-{uuid.uuid4()}"

    session_storage = SessionStorage()
    context = session_storage.load_context(session_id)
    
    context.state["user_request"] = input_text
    
    executor = WorkflowExecutor(wf)
    
    async def _run():
        print(f"Starting workflow: {wf.name} (Session: {session_id})")
        async for event in executor.run_stream(context):
            if event.type == "node_start":
                print(f"NODE: {event.data['node_id']} ({event.data['agent']})")
            elif event.type == "router_decision":
                print(f"ROUTER: {event.data['node_id']} -> {event.data['next_node']} (condition: {event.data['value']})")
            elif event.type == "text_chunk":
                if stream:
                    print(event.text, end="", flush=True)
            elif event.type == "node_end":
                if not stream:
                    print(f"OUTPUT: {event.data.get('output')}")
                print("\n") # Newline after chunks
            elif event.type == "workflow_end":
                print("WORKFLOW END")

    asyncio.run(_run())

if __name__ == "__main__":
    app()
