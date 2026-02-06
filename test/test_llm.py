import os
import asyncio
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from datagent.llms.registry import LLMRegistry

console = Console()

async def run_test_llm():
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

if __name__ == "__main__":
    from datagent.bootstrap import bootstrap_app
    bootstrap_app()
    asyncio.run(run_test_llm())
