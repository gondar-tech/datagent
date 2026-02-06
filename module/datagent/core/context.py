from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid

@dataclass(frozen=True)
class WorkflowContext:
    session_id: str
    state: Dict[str, Any] = field(default_factory=dict)
    
    def update(self, updates: Dict[str, Any]) -> 'WorkflowContext':
        new_state = self.state.copy()
        new_state.update(updates)
        return WorkflowContext(session_id=self.session_id, state=new_state)
