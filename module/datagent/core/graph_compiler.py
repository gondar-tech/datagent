from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from .yaml_workflow_loader import WorkflowDefinition
from ..agents.registry import AgentRegistry

# Attempt to import langgraph, mock if not present for the sake of structure
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    class StateGraph:
        def __init__(self, state_schema): pass
        def add_node(self, name, func): pass
        def add_edge(self, start, end): pass
        def set_entry_point(self, name): pass
        def compile(self): return self
    END = "end"

@dataclass
class CompiledGraph:
    runnable: Any # The compiled LangGraph runnable

class GraphCompiler:
    def __init__(self):
        pass

    def compile(self, definition: WorkflowDefinition) -> CompiledGraph:
        """
        Compiles a YAML WorkflowDefinition into a LangGraph executable.
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is not installed. Cannot compile graph.")

        # 1. Define State
        # For now, we use a simple dict as state, but strictly typed per agent would be better.
        workflow_state = Dict[str, Any]

        # 2. Initialize Graph
        workflow = StateGraph(workflow_state)

        # 3. Add Nodes
        for node_id, node in definition.nodes.items():
            # We need to wrap the agent execution in a function that matches LangGraph's signature
            # (state) -> new_state
            
            async def _node_executor(state: Dict[str, Any], _node=node):
                # Resolve inputs from state
                # This logic replicates WorkflowExecutor's input resolution but inside the graph node
                agent_name = _node.agent_name
                agent = AgentRegistry.instantiate(agent_name, name=_node.id)
                
                # Input resolution logic (simplified for now)
                # In a real LangGraph, we'd probably use the state directly or a transformation
                inputs = {} 
                # ... resolution logic here ...
                # For now, we assume state contains the inputs directly or we pass the whole state
                
                # This is a placeholder for the actual agent execution binding
                # output = await agent.a_run(...)
                # return {_node.id: output}
                return {f"{_node.id}_output": "executed"}

            workflow.add_node(node.id, _node_executor)

        # 4. Add Edges
        # We need to traverse the graph to add edges
        # The YAML definition has 'next_nodes'
        
        # We assume start_node is the entry point
        workflow.set_entry_point(definition.start_node)

        visited = set()
        queue = [definition.start_node]
        
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)
            
            node = definition.nodes.get(current_id)
            if not node:
                continue
                
            if node.next_nodes:
                for next_id in node.next_nodes:
                    workflow.add_edge(current_id, next_id)
                    queue.append(next_id)
            else:
                workflow.add_edge(current_id, END)

        # 5. Compile
        app = workflow.compile()
        return CompiledGraph(runnable=app)
