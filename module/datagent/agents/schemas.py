from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.context import WorkflowContext

@dataclass(frozen=True, kw_only=True)
class BasePrompt(ABC):
    email: str
    name: str
    query: str
    data_urls: list[str] = field(default_factory=list)

@dataclass(frozen=True, kw_only=True)
class BaseMessage(ABC):
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    session_id: str = field(default="default-session")
    role: str
    content: str = None

@dataclass(frozen=True, kw_only=True)
class UserMessage(BaseMessage):
    role: str = "user"

@dataclass(frozen=True, kw_only=True)
class AssistantMessage(BaseMessage):
    role: str = "assistant"
    agent_name: str
    node_id: str

@dataclass(frozen=True, kw_only=True)
class AgentInput(BaseMessage):
    role: str = "user"
    history: list[BaseMessage] = field(default_factory=list)
    prompt: BasePrompt

@dataclass(frozen=True, kw_only=True)
class AgentOutput(BaseMessage):
    role: str = "agent"
    content: str = None

@dataclass(frozen=True, kw_only=True)
class StreamingEvent(AgentOutput):
    agent_name: str
    type: str = "streaming"
    data: dict = field(default_factory=dict)

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

@dataclass(frozen=True, kw_only=True)
class ContextUpdateEvent(StreamingEvent):
    type: str = "context_update"
    context: WorkflowContext

@dataclass(frozen=True, kw_only=True)
class AgentOutputEvent(StreamingEvent):
    type: str = "agent_output"
    output: AgentOutput