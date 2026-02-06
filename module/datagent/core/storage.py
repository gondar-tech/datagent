from typing import Optional
from .context import WorkflowContext
from ..db.repositories.session import SessionRepository
from ..db.fs import FileSystemDB

class SessionStorage:
    """
    Adapter class for Session persistence.
    Delegates to the SessionRepository in the db module.
    """
    def __init__(self, storage_dir: str = None):
        # If storage_dir is provided, we use it for the FileSystemDB
        # Otherwise, FileSystemDB defaults to module/datagent/db/storage
        db_instance = FileSystemDB(root_dir=storage_dir) if storage_dir else None
        
        # If no custom dir, use the default singleton db from the module 
        # (or create new one if needed, but SessionRepository defaults to singleton db)
        if db_instance:
            self.repo = SessionRepository(database=db_instance)
        else:
            self.repo = SessionRepository()

    def save_context(self, context: WorkflowContext):
        self.repo.save(context)

    def load_context(self, session_id: str) -> WorkflowContext:
        return self.repo.load(session_id)
