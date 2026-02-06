from typing import Optional, List, Any, Dict
from ...core.context import WorkflowContext
from ...core.serialization import serialize, deserialize
from ..fs import db, FileSystemDB

class SessionRepository:
    """
    Repository for managing WorkflowContext sessions using FileSystemDB.
    """
    COLLECTION = "sessions"

    def __init__(self, database: FileSystemDB = db):
        self.db = database

    def save(self, context: WorkflowContext) -> None:
        """Save a workflow context session."""
        data = {
            "session_id": context.session_id,
            "state": serialize(context.state),
            "history": serialize(context.history)
        }
        self.db.save(self.COLLECTION, context.session_id, data)

    def load(self, session_id: str) -> WorkflowContext:
        """
        Load a workflow context session. 
        Returns a new empty context if not found.
        """
        data = self.db.load(self.COLLECTION, session_id)
        if data:
            return WorkflowContext(
                session_id=data.get("session_id", session_id),
                state=deserialize(data.get("state", {})),
                history=deserialize(data.get("history", []))
            )
        return WorkflowContext(session_id=session_id)

    def delete(self, session_id: str) -> None:
        """Delete a session."""
        self.db.delete(self.COLLECTION, session_id)

    def list_sessions(self) -> List[str]:
        """List all available session IDs."""
        return self.db.list_ids(self.COLLECTION)
