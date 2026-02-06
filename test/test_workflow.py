import asyncio
import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from datagent.core.yaml_workflow_loader import YamlWorkflowLoader
from datagent.core.workflow_executor import WorkflowExecutor
from datagent.core.storage import SessionStorage
from datagent.agents.schemas import BasePrompt

console = Console()
app = typer.Typer()

async def run_test_workflow_async(workflow_file_path: str = None, stream: bool = True):
    console.print(Panel("Workflow Testing", style="bold green"))

    loader = YamlWorkflowLoader()
    workflow_def = loader.load(workflow_file_path)
    
    session_storage = SessionStorage()
    session_id = Prompt.ask("[yellow]Enter Session ID[/yellow]", default="test-session")

    while True:
        try:
            console.print(f"\n[bold cyan]--- Workflow Session: {session_id} ---[/bold cyan]")
            user_request = Prompt.ask("\n[yellow]Enter user request (or 'quit', 'exit' to return)[/yellow]", default="Build a simple calculator")
            
            if user_request.lower() in ['quit', 'exit']:
                break

            # Load context from storage
            current_context = session_storage.load_context(session_id)

            # Create executor per iteration
            executor = WorkflowExecutor(workflow_def)
            
            console.print(f"[dim]Loaded session history: {len(current_context.history)} items[/dim]")

            console.print("[bold]Starting Workflow Execution...[/bold]")
            
            prompt = BasePrompt(
                name="Test User",
                email="test@example.com",
                query=user_request
            )
            
            try:
                # Pass the loaded context
                async for event in executor.run_stream(prompt, current_context):
                    if event.type == "node_start":
                        current_agent = event.node_id
                        node_id = event.node_id
                        console.print(Panel(f"Starting Node: [bold]{node_id}[/bold] (Agent: {current_agent})", border_style="blue"))
                    
                    elif event.type == "node_end":
                        console.print(f"[dim]Node {node_id} finished.[/dim]")
                    
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
                        console.print(f"[bold green]Workflow Ended[/bold green]")
                        
                console.print("\n[bold green]Workflow Completed Successfully.[/bold green]")
                console.print(f"[dim]Session History Items: {len(current_context.history)}[/dim]")

            except Exception as e:
                console.print(f"\n[bold red]Workflow Runtime Error:[/bold red] {e}")
                import traceback
                traceback.print_exc()
        
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupted by user. Returning...[/bold yellow]")
            break

@app.command()
def main(
    workflow_file: str = typer.Argument("workflows/workflow.yaml", help="Path to workflow YAML file"),
    stream: bool = typer.Option(True, help="Enable streaming output"),
):
    from datagent.bootstrap import bootstrap_app
    bootstrap_app()
    asyncio.run(run_test_workflow_async(workflow_file, stream=stream))

if __name__ == "__main__":
    app()
