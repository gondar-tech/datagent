import os
import json
import shutil
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

class FileSystemDB:
    """
    A simple file-based database implementation that mimics a structured store.
    It stores data in JSON files within a specified root directory.
    """
    
    def __init__(self, root_dir: str = None):
        self.root_dir = Path(root_dir or "storage")    
        self._ensure_root()
        
    def _ensure_root(self):
        """Ensure the storage root directory exists."""
        if not self.root_dir.exists():
            self.root_dir.mkdir(parents=True, exist_ok=True)
            
    def _get_collection_path(self, collection: str) -> Path:
        """Get the path for a specific collection (directory)."""
        path = self.root_dir / collection
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path
    
    def _get_doc_path(self, collection: str, doc_id: str) -> Path:
        """Get the path for a specific document (file)."""
        return self._get_collection_path(collection) / f"{doc_id}.json"

    def save(self, collection: str, doc_id: str, data: Dict[str, Any]):
        """Save a document to a collection."""
        path = self._get_doc_path(collection, doc_id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def load(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Load a document from a collection."""
        path = self._get_doc_path(collection, doc_id)
        if not path.exists():
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            # log error?
            return None

    def delete(self, collection: str, doc_id: str):
        """Delete a document."""
        path = self._get_doc_path(collection, doc_id)
        if path.exists():
            path.unlink()
            
    def list_ids(self, collection: str) -> List[str]:
        """List all document IDs in a collection."""
        path = self._get_collection_path(collection)
        return [f.stem for f in path.glob("*.json")]

# Singleton instance for easy access, configurable
db = FileSystemDB()
