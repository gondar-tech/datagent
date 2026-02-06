from __future__ import annotations

from dataclasses import dataclass
from .context import WorkflowContext
from ..agents.schemas import StreamingEvent, AgentOutput

@dataclass(frozen=True, kw_only=True)
class WorkflowEndEvent(StreamingEvent):
    type: str = "workflow_end"
    context: WorkflowContext

@dataclass(frozen=True, kw_only=True)
class RouterDecisionEvent(StreamingEvent):
    type: str = "router_decision"
    node_id: str
    next_node: str
    condition: str
    value: bool = False

@dataclass(frozen=True, kw_only=True)
class NodeStartEvent(StreamingEvent):
    type: str = "node_start"
    node_id: str

@dataclass(frozen=True, kw_only=True)
class NodeEndEvent(StreamingEvent):
    type: str = "node_end"
    node_id: str
    output: AgentOutput