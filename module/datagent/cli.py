import click
import asyncio
import sys
import logging
from datagent.bootstrap import bootstrap_app
from datagent.core.yaml_workflow_loader import YamlWorkflowLoader
from datagent.core.workflow_executor import WorkflowExecutor
from datagent.core.context import WorkflowContext
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Import agents to register them
import datagent.agents.greeting.agent
import datagent.agents.planner.agent
import datagent.agents.code_generator.generator
import datagent.agents.code_validator.validator
import datagent.agents.trainer.agent
import datagent.agents.inferencer.agent
import datagent.agents.training_planner.agent
import datagent.agents.data_processor.agent
import datagent.agents.orchestrator.agent

console = Console()

@click.group()
def cli():
    """Datagent CLI"""
    pass

@cli.command()
@click.argument('workflow_file')
def run(workflow_file):
    """Run a workflow from a YAML file."""
    # Initialize app (logs, db, etc)
    bootstrap_app()
    
    print("DEBUG: CLI Run Command Started")
    console.print(f"[bold green]Running workflow:[/bold green] {workflow_file}")
    
    loader = YamlWorkflowLoader()
    try:
        workflow_def = loader.load(workflow_file)
        console.print(f"[dim]Workflow loaded: {workflow_def.name}[/dim]")
    except Exception as e:
        console.print(f"[bold red]Error loading workflow:[/bold red] {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    executor = WorkflowExecutor(workflow_def)
    initial_context = WorkflowContext(session_id="cli-session")
    
    async def _run():
        current_agent = "System"
        
        # Simple streaming output
        try:
            async for event in executor.run_stream(initial_context):
                if event.type == "node_start":
                    current_agent = event.data.get("agent", "Unknown")
                    node_id = event.data.get("node_id")
                    console.print(Panel(f"Starting Node: [bold]{node_id}[/bold] (Agent: {current_agent})", border_style="blue"))
                
                elif event.type == "node_end":
                    console.print(f"[dim]Node finished.[/dim]")
                
                elif event.type == "text_chunk":
                    content = event.content
                    if content:
                        console.print(content, end="")
                
                elif event.type == "tool_start":
                    console.print(f"[yellow]Tool Call:[/yellow] {event.data.get('tool_name')}")
                
                elif event.type == "tool_end":
                    console.print(f"[dim]Tool Result:[/dim] {event.data.get('output')}")
        except Exception as e:
             console.print(f"[bold red]Runtime Error:[/bold red] {e}")
             import traceback
             traceback.print_exc()

        console.print("\n[bold green]Workflow Completed.[/bold green]")
        
    asyncio.run(_run())

if __name__ == '__main__':
    cli()
