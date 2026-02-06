import asyncio
import os
import sys
from typing import Dict, Any

# Ensure module is in path
sys.path.append(os.path.join(os.getcwd(), "module"))

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live

from datagent.llms.registry import LLMRegistry
from datagent.bootstrap import bootstrap_app
from datagent.core.yaml_workflow_loader import YamlWorkflowLoader
from datagent.core.workflow_executor import WorkflowExecutor
from datagent.core.context import WorkflowContext

import datagent.llms.openai.client
import datagent.llms.groq.client

# Import agents for registration
import datagent.agents.greeting.agent
import datagent.agents.planner.agent
import datagent.agents.code_generator.generator
import datagent.agents.code_validator.validator

console = Console()

async def test_llm():
    console.print(Panel("LLM Testing", style="bold blue"))
    provider = Prompt.ask("Select Provider", choices=["openai", "groq"], default="openai")
    model = Prompt.ask("Enter Model", default="gpt-3.5-turbo" if provider == "openai" else "llama3-8b-8192")
    
    api_key_env = f"{provider.upper()}_API_KEY"
    api_key = os.getenv(api_key_env)
    
    if not api_key:
        api_key = Prompt.ask(f"Enter {provider} API Key", password=True)
    
    try:
        llm = LLMRegistry.instantiate(provider, api_key=api_key, model=model)
        
        while True:
            prompt = Prompt.ask("\nEnter prompt (or 'exit')")
            if prompt.lower() == 'exit':
                break
                
            console.print("[bold green]Streaming Response:[/bold green]")
            response_text = ""
            try:
                async for chunk in llm.generate_stream(prompt):
                    if chunk.content:
                        console.print(chunk.content, end="")
                        response_text += chunk.content
                console.print("\n")
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {e}")

    except Exception as e:
        console.print(f"[bold red]Initialization Error:[/bold red] {e}")

async def test_rag():
    console.print(Panel("RAG Testing (Placeholder)", style="bold yellow"))
    console.print("RAG testing implementation coming soon...")

async def test_workflow():
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

    while True:
        try:
            console.print("\n[bold cyan]--- New Workflow Session ---[/bold cyan]")
            user_request = Prompt.ask("\nEnter user request for workflow (or 'quit', 'exit' to return to menu)", default="Build a simple calculator")
            
            if user_request.lower() in ['quit', 'exit']:
                break

            try:
                workflow_def = loader.load(workflow_file)
                
                # Override the start node input mapping for dynamic user request
                # This is a bit of a hack for testing, normally we'd pass it in context
                start_node = workflow_def.nodes[workflow_def.start_node]
                start_node.input_mapping['user_request'] = user_request
                
                console.print(f"[dim]Workflow loaded: {workflow_def.name}[/dim]")
            except Exception as e:
                console.print(f"[bold red]Error loading workflow:[/bold red] {str(e)}")
                continue

            executor = WorkflowExecutor(workflow_def)
            initial_context = WorkflowContext(session_id="test-session")

            console.print("[bold]Starting Workflow Execution...[/bold]")
            
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
                        
                console.print("\n[bold green]Workflow Completed Successfully.[/bold green]")

            except Exception as e:
                console.print(f"\n[bold red]Workflow Runtime Error:[/bold red] {e}")
                import traceback
                traceback.print_exc()
        
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupted by user. Returning to menu...[/bold yellow]")
            break

async def main():
    bootstrap_app()
    
    while True:
        console.clear()
        console.print(Panel("Datagent Console Tester", style="bold magenta"))
        console.print("1. Test LLM (OpenAI/Groq)")
        console.print("2. Test RAG")
        console.print("3. Test Workflow (CLI -> Agents)")
        console.print("4. Exit")
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            await test_llm()
        elif choice == "2":
            await test_rag()
        elif choice == "3":
            await test_workflow()
        elif choice == "4":
            break
        
        if Confirm.ask("Return to menu?"):
            continue
        else:
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting...[/bold red]")
