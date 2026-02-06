from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import yaml

@dataclass
class WorkflowNode:
    id: str
    type: str = "agent"  # agent, router, end
    agent_name: Optional[str] = None
    input_mapping: Dict[str, str] = field(default_factory=dict)
    next_nodes: List[str] = field(default_factory=list)
    
    # Router specific properties
    condition: Optional[str] = None
    routes: Dict[str, str] = field(default_factory=dict)
    default_route: Optional[str] = None
    
    # Agent config
    config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowDefinition:
    name: str
    nodes: Dict[str, WorkflowNode]
    start_node: str
    config: Dict[str, Any] = field(default_factory=dict)

class YamlWorkflowLoader:
    def load(self, file_path: str) -> WorkflowDefinition:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            
        nodes_data = data.get('nodes', {})
        nodes = {}
        
        # Handle if nodes is a list or dict
        if isinstance(nodes_data, list):
            for node_data in nodes_data:
                node = self._parse_node(node_data)
                nodes[node.id] = node
        elif isinstance(nodes_data, dict):
            for key, node_data in nodes_data.items():
                # If ID is missing in value, use the key
                if 'id' not in node_data:
                    node_data['id'] = key
                node = self._parse_node(node_data)
                nodes[node.id] = node
        
        # Parse edges if present
        edges_data = data.get('edges', [])
        for edge in edges_data:
            from_id = edge.get('from')
            to_id = edge.get('to')
            condition_val = edge.get('condition') # Used for router branches
            
            if from_id in nodes and to_id:
                source_node = nodes[from_id]
                
                if source_node.type == 'router':
                    # If it's a router, we expect a condition value (the route key)
                    # Unless it's the default route?
                    if condition_val:
                        source_node.routes[str(condition_val)] = to_id
                    elif edge.get('default', False) or 'default' in edge:
                         # explicitly marked as default
                         source_node.default_route = to_id
                    else:
                        # Fallback: if no condition, maybe it's the default?
                        # Or user forgot condition.
                        # Let's assume default if no condition provided for router?
                        if not source_node.default_route:
                            source_node.default_route = to_id
                else:
                    # Standard node, just append to next_nodes if not already there
                    if to_id not in source_node.next_nodes:
                        source_node.next_nodes.append(to_id)

        # Parse global config
        # We look for 'config' key, and also merge 'default_llm_config' into it for backward compat/convenience
        global_config = data.get('config', {})
        
        # Also grab top-level fields that might be config-like if user put them there
        if 'default_llm_config' in data:
            global_config['llm_config'] = data['default_llm_config']
        elif 'llm_config' in data: # Support top-level llm_config shorthand
            global_config['llm_config'] = data['llm_config']

        return WorkflowDefinition(
            name=data.get('name', 'unnamed'),
            nodes=nodes,
            start_node=data.get('start_node'),
            config=global_config
        )

    def _parse_node(self, node_data: Dict[str, Any]) -> WorkflowNode:
        # Normalize next_nodes
        next_val = node_data.get('next_nodes') or node_data.get('next', [])
        if isinstance(next_val, str):
            next_nodes = [next_val]
        else:
            next_nodes = next_val

        return WorkflowNode(
            id=node_data.get('id'),
            type=node_data.get('type', 'agent'),
            agent_name=node_data.get('agent') or node_data.get('agent_name') or node_data.get('agent_id'),
            input_mapping=node_data.get('input_mapping') or node_data.get('inputs', {}),
            next_nodes=next_nodes,
            condition=node_data.get('condition'),
            routes=node_data.get('routes', {}),
            default_route=node_data.get('default'),
            config=node_data.get('config', {})
        )
