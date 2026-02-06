from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class Document:
    content: str
    metadata: Dict[str, Any]
    id: Optional[str] = None
    embedding: Optional[List[float]] = None

class BaseVectorStore(ABC):
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to store and return IDs."""
        pass

    @abstractmethod
    async def search(self, query_embedding: List[float], k: int = 4) -> List[Document]:
        """Search for similar documents."""
        pass
