import os
import asyncio
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from datagent.core.yaml_workflow_loader import YamlWorkflowLoader
from datagent.core.workflow_executor import WorkflowExecutor
from datagent.core.storage import SessionStorage

# Ensure agents are registered
import datagent.agents.greeting.agent
import datagent.agents.planner.agent
import datagent.agents.code_generator.generator
import datagent.agents.code_validator.validator
import datagent.agents.data_processor.agent
import datagent.agents.extra_topic.agent

console = Console()

async def run_test_workflow():
    console.print(Panel("Workflow Testing", style="bold green"))
    
    workflow_file = "workflows/test_workflow.yaml"
    if not os.path.exists(workflow_file):
        console.print(f"[bold red]Workflow file not found:[/bold red] {workflow_file}")
        return

    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
         console.print("[bold yellow]Warning: OPENAI_API_KEY not set. Some agents might fail.[/bold yellow]")
         key = Prompt.ask("Enter OpenAI API Key (optional)", password=True)
         if key:
             os.environ["OPENAI_API_KEY"] = key

    if not os.getenv("GROQ_API_KEY"):
         console.print("[bold yellow]Warning: GROQ_API_KEY not set. Agents using Groq might fail.[/bold yellow]")
         key = Prompt.ask("Enter Groq API Key (optional)", password=True)
         if key:
             os.environ["GROQ_API_KEY"] = key

    loader = YamlWorkflowLoader()
    
    # Initialize session storage
    session_storage = SessionStorage()
    session_id = Prompt.ask("Enter Session ID", default="test-session")

    while True:
        try:
            console.print(f"\n[bold cyan]--- Workflow Session: {session_id} ---[/bold cyan]")
            user_request = Prompt.ask("\nEnter user request (or 'quit', 'exit' to return)", default="Build a simple calculator")
            
            if user_request.lower() in ['quit', 'exit']:
                break
            
            try:
                workflow_def = loader.load(workflow_file)
            except Exception as e:
                console.print(f"[bold red]Error loading workflow:[/bold red] {str(e)}")
                continue

            # Update start node input mapping for this run
            start_node = workflow_def.nodes[workflow_def.start_node]
            start_node.input_mapping['user_request'] = user_request

            # Create executor per iteration
            executor = WorkflowExecutor(workflow_def)
            
            # Load context from storage
            current_context = session_storage.load_context(session_id)
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
                        if content:
                            console.print(content, end="")
                    
                    elif event.type == "tool_start":
                        console.print(f"[yellow]Tool Call:[/yellow] {event.data.get('tool_name')}")
                    
                    elif event.type == "tool_end":
                        console.print(f"[dim]Tool Result:[/dim] {event.data.get('output')}")
                    
                    elif event.type == "context_update":
                        # Update our local context reference
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

if __name__ == "__main__":
    from datagent.bootstrap import bootstrap_app
    bootstrap_app()
    asyncio.run(run_test_workflow())
