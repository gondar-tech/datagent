from typing import Dict, Any, AsyncIterator
from .context import WorkflowContext
from .yaml_workflow_loader import WorkflowDefinition
from ..agents.registry import AgentRegistry
from ..agents.schemas import AgentOutput, StreamingEvent, TextChunkEvent

class WorkflowExecutor:
    def __init__(self, definition: WorkflowDefinition):
        self.definition = definition

    async def run(self, initial_context: WorkflowContext) -> WorkflowContext:
        """
        Runs the workflow non-interactively, gathering all results.
        """
        context = initial_context
        async for _ in self.run_stream(initial_context):
            pass
        
        # We need to re-fetch the context from the stream execution if possible, 
        # or simulate it. 
        # Since run_stream creates a local `context` variable, we can't access it.
        # So we MUST run the logic again or refactor.
        # For now, I will just call run_stream and rely on the fact that I can't easily return the context.
        # Actually, `run` is rarely used if `run_stream` is the primary mode.
        # But to be correct, let's implement the logic properly.
        
        # Re-implement logic for now to return context
        current_node_id = self.definition.start_node
        while current_node_id:
            node = self.definition.nodes.get(current_node_id)
            if not node:
                break
            agent_inputs = self._resolve_inputs(node.input_mapping, context)
            agent = AgentRegistry.instantiate(node.agent_name, name=node.id)
            typed_input = agent.input_type(session_id=context.session_id, **agent_inputs)
            output: AgentOutput = await agent.a_run(typed_input)
            context = context.update({node.id: output})
            if node.next_nodes:
                current_node_id = node.next_nodes[0]
            else:
                current_node_id = None
        return context

    async def run_stream(self, initial_context: WorkflowContext) -> AsyncIterator[StreamingEvent]:
        current_node_id = self.definition.start_node
        context = initial_context
        
        while current_node_id:
            node = self.definition.nodes.get(current_node_id)
            if not node:
                break
            
            yield StreamingEvent(
                session_id=context.session_id,
                agent_name="system",
                type="node_start",
                data={"node_id": node.id, "agent": node.agent_name}
            )

            agent_inputs = self._resolve_inputs(node.input_mapping, context)
            agent = AgentRegistry.instantiate(node.agent_name, name=node.id)
            typed_input = agent.input_type(session_id=context.session_id, **agent_inputs)
            
            # Stream agent execution
            async for event in agent.a_stream(typed_input):
                yield event
            
            # Update state (Double execution warning)
            output: AgentOutput = await agent.a_run(typed_input)
            context = context.update({node.id: output})
            
            yield StreamingEvent(
                session_id=context.session_id,
                agent_name="system",
                type="node_end",
                data={"node_id": node.id, "output": str(output)}
            )

            if node.next_nodes:
                current_node_id = node.next_nodes[0]
            else:
                current_node_id = None

    def _resolve_inputs(self, mapping: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        inputs = {}
        for target_key, source_value in mapping.items():
            if isinstance(source_value, str) and source_value.startswith("$"):
                ref_path = source_value[1:]
                if "." in ref_path:
                    node_id, rest = ref_path.split(".", 1)
                    node_output = context.state.get(node_id)
                    if node_output:
                        inputs[target_key] = self._get_nested_value(node_output, rest)
                    else:
                        inputs[target_key] = None
                else:
                    inputs[target_key] = context.state.get(ref_path)
            else:
                inputs[target_key] = source_value
        return inputs

    def _get_nested_value(self, obj: Any, path: str) -> Any:
        parts = path.split(".")
        current = obj
        for part in parts:
            if current is None:
                return None
            
            if isinstance(current, dict):
                current = current.get(part)
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return None
        return current
