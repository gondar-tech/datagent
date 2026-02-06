from ..agents.schemas import StreamingEvent

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
    agent: str