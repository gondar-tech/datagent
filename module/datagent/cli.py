import typer
import asyncio
import uuid
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from .settings import settings
from .bootstrap import bootstrap_app
from .core.workflow_executor import WorkflowExecutor
from .core.yaml_workflow_loader import YamlWorkflowLoader
from .core.storage import SessionStorage
from .agents.schemas import BasePrompt

app = typer.Typer()
console = Console()

@app.command()
def info():
    """Display application information."""
    console.print(Panel(f"Environment: {settings.ENV}\nDebug Mode: {settings.DEBUG}", title="Datagent Info", border_style="blue"))

@app.command()
def run(
    workflow_path: str = typer.Argument("workflows/workflow.yaml", help="Path to workflow YAML file"),
    input_text: str = typer.Option(..., "--input", "-i", help="Initial user input."),
    session_id: Optional[str] = typer.Option(None, "--session-id", "-s", help="Session ID"),
    stream: bool = typer.Option(True, "--stream/--no-stream", help="Stream output tokens"),
    user_name: str = typer.Option("CLI User", "--name", "-n", help="User name"),
    user_email: str = typer.Option("cli@datagent.ai", "--email", "-e", help="User email")
):
    """Run a workflow from a YAML file."""
    bootstrap_app()
    
    loader = YamlWorkflowLoader()
    try:
        workflow_def = loader.load(workflow_path)
    except Exception as e:
        console.print(f"[bold red]Error loading workflow:[/bold red] {e}")
        raise typer.Exit(code=1)

    if not session_id:
        session_id = f"cli-run-{uuid.uuid4()}"

    session_storage = SessionStorage()
    
    async def run():
        try:
            console.print(f"\n[bold cyan]--- Workflow Session: {session_id} ---[/bold cyan]")
            console.print(f"[bold]User Input:[/bold] {input_text}")

            # 2. Load Context
            current_context = session_storage.load_context(session_id)
            console.print(f"[dim]Loaded session history: {len(current_context.history)} items[/dim]")

            # 3. Prepare Executor
            executor = WorkflowExecutor(workflow_def)
            prompt = BasePrompt(
                name=user_name,
                email=user_email,
                query=input_text
            )

            # 4. Execute
            console.print("[bold]Starting Workflow Execution...[/bold]")
            try:
                async for event in executor.run_stream(prompt, current_context):
                    if event.type == "node_start":
                        node_id = event.node_id
                        agent_name = event.data.get('agent', 'unknown')
                        console.print(Panel(f"Starting Node: [bold]{node_id}[/bold] (Agent: {agent_name})", border_style="blue"))
                    
                    elif event.type == "node_end":
                        console.print(f"[dim]Node {event.node_id} finished.[/dim]")
                    
                    elif event.type == "router_decision":
                            console.print(f"[bold magenta]Router Decision:[/bold magenta] {event.condition} = {event.value} -> {event.next_node}")
                    
                    elif event.type == "text_chunk":
                        content = event.content
                        role = getattr(event, "role", "assistant")
                        style = "green"
                        if role == "agent":
                            style = "dim"
                        elif role == "assistant":
                            style = "green"
                            
                        if content and stream:
                            console.print(content, style=style, end="")
                    
                    elif event.type == "tool_start":
                        console.print(f"[yellow]Tool Call:[/yellow] {event.data.get('tool_name')}")
                    
                    elif event.type == "tool_end":
                        console.print(f"[dim]Tool Result:[/dim] {event.data.get('output')}")
                    
                    elif event.type == "context_update":
                        console.print(f"[dim]Context Update:[/dim] {event}")
                        updated_context = event.context
                        session_storage.save_context(updated_context)
                        current_context = updated_context

                    elif event.type == "workflow_end":
                        console.print(f"\n[bold green]Workflow Ended[/bold green]")

                console.print("\n[bold green]Workflow Completed Successfully.[/bold green]")
                console.print(f"[dim]Session History Items: {len(current_context.history)}[/dim]")

            except Exception as e:
                console.print(f"\n[bold red]Workflow Runtime Error:[/bold red] {e}")

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupted by user. Exiting...[/bold yellow]")
        except Exception as e:
            console.print(f"\n[bold red]System Error:[/bold red] {e}")

    asyncio.run(run())

if __name__ == "__main__":
    app()
