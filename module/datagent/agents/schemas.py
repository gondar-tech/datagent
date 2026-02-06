from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC
import uuid

@dataclass(frozen=True, kw_only=True)
class BaseMessage(ABC):
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    session_id: str = field(default="default-session")

@dataclass(frozen=True, kw_only=True)
class AgentInput(BaseMessage):
    pass

@dataclass(frozen=True, kw_only=True)
class AgentOutput(BaseMessage):
    pass

@dataclass(frozen=True, kw_only=True)
class StreamingEvent(BaseMessage):
    agent_name: str
    type: str
    data: dict = field(default_factory=dict)
    content: str = "" # Optional content for simple events

@dataclass(frozen=True, kw_only=True)
class TextChunkEvent(StreamingEvent):
    chunk_index: int = 0
    type: str = "text_chunk"

@dataclass(frozen=True, kw_only=True)
class ToolStartEvent(StreamingEvent):
    type: str = "tool_start"

@dataclass(frozen=True, kw_only=True)
class ToolEndEvent(StreamingEvent):
    type: str = "tool_end"
