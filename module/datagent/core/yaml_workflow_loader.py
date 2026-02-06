from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import yaml

@dataclass
class WorkflowNode:
    id: str
    agent_name: str
    input_mapping: Dict[str, str] = field(default_factory=dict)
    next_nodes: List[str] = field(default_factory=list)

@dataclass
class WorkflowDefinition:
    name: str
    nodes: Dict[str, WorkflowNode]
    start_node: str

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
                
        return WorkflowDefinition(
            name=data.get('name', 'unnamed'),
            nodes=nodes,
            start_node=data.get('start_node')
        )

    def _parse_node(self, node_data: Dict[str, Any]) -> WorkflowNode:
        # Support both alias styles for compatibility
        return WorkflowNode(
            id=node_data.get('id'),
            agent_name=node_data.get('agent_name') or node_data.get('agent'),
            input_mapping=node_data.get('input_mapping') or node_data.get('inputs', {}),
            next_nodes=node_data.get('next_nodes') or node_data.get('next', [])
        )
