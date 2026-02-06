from typing import List, Optional
import os
from langchain_openai import OpenAIEmbeddings
from .embedder import BaseEmbedder

class OpenAIEmbedder(BaseEmbedder):
    def __init__(self, model: str = "text-embedding-3-small", api_key: Optional[str] = None):
        self.model = model
        self.embeddings = OpenAIEmbeddings(
            model=model,
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return await self.embeddings.aembed_documents(texts)

    async def embed_query(self, text: str) -> List[float]:
        return await self.embeddings.aembed_query(text)
