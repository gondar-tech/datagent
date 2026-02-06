import asyncio
import os
import json
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from datagent.agents.registry import AgentRegistry

# Ensure agents are registered
import datagent.agents.greeting.agent
import datagent.agents.planner.agent
import datagent.agents.code_generator.generator
import datagent.agents.code_validator.validator

console = Console()

async def run_test_agents():
    console.print(Panel("Individual Agent Testing", style="bold magenta"))
    
    # List available agents
    available_agents = AgentRegistry.list_agents()
    if not available_agents:
        console.print("[red]No agents registered![/red]")
        return
        
    console.print("Available Agents:")
    for i, name in enumerate(available_agents):
        console.print(f"{i+1}. {name}")
        
    choice = Prompt.ask("Select Agent", choices=[str(i+1) for i in range(len(available_agents))])
    agent_name = available_agents[int(choice)-1]
    
    console.print(f"[bold]Selected Agent: {agent_name}[/bold]")
    
    # Configure Agent
    config_str = Prompt.ask("Enter Agent Config (JSON) or press Enter for default", default="{}")
    try:
        config = json.loads(config_str)
    except Exception:
        console.print("[red]Invalid JSON, using empty config[/red]")
        config = {}
        
    # Instantiate
    try:
        agent = AgentRegistry.instantiate(agent_name, agent_id="test-agent", **config)
    except Exception as e:
        console.print(f"[red]Failed to instantiate agent: {e}[/red]")
        return
        
    while True:
        user_input = Prompt.ask(f"\nEnter input for {agent_name} (or 'exit')")
        if user_input.lower() == 'exit':
            break
            
        # Try to guess input format. Most agents take a dict or string.
        # We'll wrap string in a standard input structure if needed, but for now passing raw input 
        # might be tricky if the agent expects a specific Pydantic model.
        # Let's assume most agents take a dict or we construct a simple one.
        
        input_data = user_input
        # Attempt to parse as JSON if it looks like it
        if user_input.strip().startswith("{"):
            try:
                input_data = json.loads(user_input)
            except:
                pass
                
        console.print("[bold green]Running...[/bold green]")
        try:
            # We use a_stream to test streaming capabilities
            async for event in agent.a_stream(input_data):
                # Just print events as they come
                console.print(event)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    from datagent.bootstrap import bootstrap_app
    bootstrap_app()
    asyncio.run(run_test_agents())
