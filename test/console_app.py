import asyncio
import sys
import os
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

# Ensure module is in path
sys.path.append(os.path.join(os.getcwd(), "module"))

from datagent.bootstrap import bootstrap_app
from datagent.settings import settings

# Placeholder imports for tests - assuming these files exist or will exist
# If they don't exist yet, we can mock them or import them conditionally
try:
    from test.test_llm import run_test_llm
except ImportError:
    run_test_llm = None

try:
    from test.test_rag import run_test_rag
except ImportError:
    run_test_rag = None

try:
    from test.test_workflow import run_test_workflow
except ImportError:
    run_test_workflow = None

try:
    from test.test_agents import run_test_agents
except ImportError:
    run_test_agents = None

console = Console()
app = typer.Typer()

async def run_async_test(test_func):
    if test_func:
        await test_func()
    else:
        console.print("[red]Test module not found or not implemented yet.[/red]")

@app.command()
def interactive():
    """Start the interactive console tester."""
    asyncio.run(main_loop())

async def main_loop():
    bootstrap_app()
    
    while True:
        console.clear()
        console.print(Panel(f"Datagent Console Tester ({settings.ENV})", style="bold magenta"))
        console.print("1. Test LLM (OpenAI/Groq)")
        console.print("2. Test RAG")
        console.print("3. Test Workflow (CLI -> Agents)")
        console.print("4. Test Individual Agents")
        console.print("5. Exit")
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            await run_async_test(run_test_llm)
        elif choice == "2":
            await run_async_test(run_test_rag)
        elif choice == "3":
            await run_async_test(run_test_workflow)
        elif choice == "4":
            await run_async_test(run_test_agents)
        elif choice == "5":
            break
        
        if not Confirm.ask("\nReturn to menu?"):
            break

if __name__ == "__main__":
    app()
