import asyncio
import sys
import os
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

# Ensure module is in path
sys.path.append(os.path.join(os.getcwd(), "module"))

from datagent.bootstrap import bootstrap_app
from test_llm import run_test_llm
from test_rag import run_test_rag
from test_workflow import run_test_workflow
from test_agents import run_test_agents

console = Console()

async def main():
    bootstrap_app()
    
    while True:
        console.clear()
        console.print(Panel("Datagent Console Tester", style="bold magenta"))
        console.print("1. Test LLM (OpenAI/Groq)")
        console.print("2. Test RAG")
        console.print("3. Test Workflow (CLI -> Agents)")
        console.print("4. Test Individual Agents")
        console.print("5. Exit")
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            await run_test_llm()
        elif choice == "2":
            await run_test_rag()
        elif choice == "3":
            await run_test_workflow()
        elif choice == "4":
            await run_test_agents()
        elif choice == "5":
            break
        
        if Confirm.ask("\nReturn to menu?"):
            continue
        else:
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting...[/bold red]")
