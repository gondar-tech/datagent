from typing import List, Dict, Any, Optional
from .base import VectorStore

class WeaviateVectorStore(VectorStore):
    def __init__(self, url: str = "http://localhost:8080", class_name: str = "CodeChunk"):
        self.url = url
        self.class_name = class_name
        # self.client = weaviate.Client(url)

    async def add_documents(self, documents: List[Dict[str, Any]]):
        # with self.client.batch as batch:
        #     for doc in documents:
        #         batch.add_data_object(doc, self.class_name)
        pass

    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        # result = self.client.query.get(self.class_name, ["content", "metadata"])...
        return []
