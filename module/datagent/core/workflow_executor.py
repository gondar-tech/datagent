from typing import Dict, Any, AsyncIterator
from .context import WorkflowContext
from .yaml_workflow_loader import WorkflowDefinition
from ..agents.registry import AgentRegistry
from ..agents.schemas import AgentOutput, StreamingEvent, TextChunkEvent, AgentOutputEvent

class WorkflowExecutor:
    def __init__(self, definition: WorkflowDefinition):
        self.definition = definition

    async def run(self, initial_context: WorkflowContext) -> WorkflowContext:
        """
        Runs the workflow non-interactively, gathering all results.
        """
        # We need to capture the final context.
        # Since run_stream creates a local variable, we can't easily get it back unless we yield it.
        # But we can reconstruct the logic for `run` or just iterate over the stream and look for context updates.
        
        context = initial_context
        async for event in self.run_stream(initial_context):
            if event.type == "context_update" and isinstance(event.data, dict) and "context" in event.data:
                context = event.data["context"]
        return context

    async def run_stream(self, initial_context: WorkflowContext) -> AsyncIterator[StreamingEvent]:
        context = initial_context
        current_node_id = self.definition.start_node

        while current_node_id:
            node = self.definition.nodes.get(current_node_id)
            if not node:
                break

            # Check node type
            if node.type == "end":
                 yield StreamingEvent(
                    session_id=context.session_id,
                    agent_name="system",
                    type="workflow_end",
                    data={"node_id": node.id}
                )
                 break

            if node.type == "router":
                # Evaluate condition
                # condition is likely a variable name like "$next_agent"
                condition_val = self._resolve_value(node.condition, context)
                
                # Determine next node
                # routes is a dict: { "greeting": "greeting_node", "planner": "planner_node" }
                next_node_id = node.routes.get(str(condition_val), node.default_route)
                
                yield StreamingEvent(
                    session_id=context.session_id,
                    agent_name="system",
                    type="router_decision",
                    data={
                        "node_id": node.id, 
                        "condition": node.condition, 
                        "value": str(condition_val), 
                        "next_node": next_node_id
                    }
                )

                current_node_id = next_node_id
                continue

            # It's an agent node
            yield StreamingEvent(
                session_id=context.session_id,
                agent_name="system",
                type="node_start",
                data={"node_id": node.id, "agent": node.agent_name}
            )

            agent_inputs = self._resolve_inputs(node.input_mapping, context)
            
            # Merge configs
            final_config = node.config.copy()
            
            # Merge global config into node config
            if self.definition.config:
                for key, global_val in self.definition.config.items():
                    if key not in final_config:
                        final_config[key] = global_val
                    else:
                        # Both exist. Shallow merge if dicts
                        local_val = final_config[key]
                        if isinstance(global_val, dict) and isinstance(local_val, dict):
                            merged = global_val.copy()
                            merged.update(local_val)
                            final_config[key] = merged
            
            # Instantiate agent with config
            agent = AgentRegistry.instantiate(node.agent_name, agent_id=node.id, **final_config)
            
            typed_input = agent.input_type(session_id=context.session_id, **agent_inputs)
            
            # Variable to capture the final output from the stream
            final_output: AgentOutput = None
            
            # Stream agent execution
            async for event in agent.a_stream(typed_input):
                yield event
                
                # Capture context updates from agent
                if event.type == "context_update" and isinstance(event.data, dict) and "context" in event.data:
                    # Merge update into current context
                    updates = event.data["context"]
                    # If updates is a dict of key-values, we assume they go into state
                    # But context.update expects {node_id: output} usually?
                    # We need to support arbitrary variable setting.
                    if isinstance(updates, dict):
                        # We merge these updates into the state. 
                        # This allows agents to set variables like "next_agent".
                        # But wait, context.update(updates) replaces/merges into state.
                        context = context.update(updates)

                # Capture final output
                if isinstance(event, AgentOutputEvent):
                    final_output = event.output

            # If no AgentOutputEvent was yielded, we might need a fallback or assume it failed?
            # For now, if final_output is None, we assume the agent implementation is legacy 
            # and might need a_run, BUT we want to avoid double execution.
            # So we strictly rely on AgentOutputEvent for now for new agents.
            
            if final_output:
                output = final_output
            else:
                # Fallback: create a generic output or empty one
                # This handles cases where agent didn't yield output event (legacy or error)
                output = AgentOutput(session_id=context.session_id)
            
            # Add to history
            context = context.update({node.id: output})
            context = context.add_history({
                "node_id": node.id,
                "agent": node.agent_name,
                "input": agent_inputs,
                "output": output
            })

            yield StreamingEvent(
                session_id=context.session_id,
                agent_name="system",
                type="node_end",
                data={"node_id": node.id, "output": str(output)}
            )
            
            # Emit context update event for the system to know state changed
            yield StreamingEvent(
                session_id=context.session_id,
                agent_name="system",
                type="context_update",
                data={"context": context}
            )

            if node.next_nodes:
                current_node_id = node.next_nodes[0]
            else:
                current_node_id = None

    def _resolve_inputs(self, mapping: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        inputs = {}
        for target_key, source_value in mapping.items():
            inputs[target_key] = self._resolve_value(source_value, context)
        return inputs

    def _resolve_value(self, source_value: Any, context: WorkflowContext) -> Any:
        if isinstance(source_value, str) and source_value.startswith("$"):
            ref_path = source_value[1:]
            
            if "." in ref_path:
                node_id, rest = ref_path.split(".", 1)
                node_output = context.state.get(node_id)
                if node_output:
                    return self._get_nested_value(node_output, rest)
                
                # Fallback: check global vars/state directly
                # If "planner.next_agent" is stored in state["next_agent"]? No.
                return None
            else:
                # Direct match
                # 1. Check if it's in state (node outputs OR variables)
                if ref_path in context.state:
                    return context.state[ref_path]
                
                # 2. Check if it's in history (not easy to access by simple key)
                return None
        return source_value

    def _get_nested_value(self, obj: Any, path: str) -> Any:
        parts = path.split(".")
        current = obj
        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current
