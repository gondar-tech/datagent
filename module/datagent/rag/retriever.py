from typing import List
from .embedder import BaseEmbedder
from .vector_store.base import BaseVectorStore, Document

class Retriever:
    def __init__(self, vector_store: BaseVectorStore, embedder: BaseEmbedder):
        self.vector_store = vector_store
        self.embedder = embedder

    async def retrieve(self, query: str, k: int = 4) -> List[Document]:
        embedding = await self.embedder.embed_query(query)
        return await self.vector_store.search(embedding, k=k)
