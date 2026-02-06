import os
import asyncio
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from datagent.core.yaml_workflow_loader import YamlWorkflowLoader
from datagent.core.workflow_executor import WorkflowExecutor
from datagent.core.storage import SessionStorage

console = Console()
app = typer.Typer()

async def run_test_workflow_async(workflow_file_path: str = None, stream: bool = True):
    console.print(Panel("Workflow Testing", style="bold green"))

    loader = YamlWorkflowLoader()
    workflow_def = loader.load(workflow_file_path)
    
    session_storage = SessionStorage()
    session_id = Prompt.ask("Enter Session ID", default="test-session")

    while True:
        try:
            console.print(f"\n[bold cyan]--- Workflow Session: {session_id} ---[/bold cyan]")
            user_request = Prompt.ask("\nEnter user request (or 'quit', 'exit' to return)", default="Build a simple calculator")
            
            if user_request.lower() in ['quit', 'exit']:
                break

            # Load context from storage
            current_context = session_storage.load_context(session_id)
            current_context.state['user_request'] = user_request

            # Create executor per iteration
            executor = WorkflowExecutor(workflow_def)
            
            console.print(f"[dim]Loaded session history: {len(current_context.history)} items[/dim]")

            console.print("[bold]Starting Workflow Execution...[/bold]")
            
            try:
                # Pass the loaded context
                async for event in executor.run_stream(current_context):
                    if event.type == "node_start":
                        current_agent = event.data.get("agent", "Unknown")
                        node_id = event.data.get("node_id")
                        console.print(Panel(f"Starting Node: [bold]{node_id}[/bold] (Agent: {current_agent})", border_style="blue"))
                    
                    elif event.type == "node_end":
                        console.print(f"[dim]Node finished.[/dim]")
                    
                    elif event.type == "router_decision":
                        console.print(f"[bold magenta]Router Decision:[/bold magenta] {event.data.get('condition')} = {event.data.get('value')} -> {event.data.get('next_node')}")

                    elif event.type == "text_chunk":
                        content = event.content
                        if content and stream:
                            console.print(content, end="")
                    
                    elif event.type == "tool_start":
                        console.print(f"[yellow]Tool Call:[/yellow] {event.data.get('tool_name')}")
                    
                    elif event.type == "tool_end":
                        console.print(f"[dim]Tool Result:[/dim] {event.data.get('output')}")
                    
                    elif event.type == "context_update":
                        # Update our local context reference
                        console.print(f"[dim]Context Update:[/dim] {event}")
                        updated_context = event.data.get("context")
                        # Save to storage immediately (or at end)
                        session_storage.save_context(updated_context)
                        current_context = updated_context
                        
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
