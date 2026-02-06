from typing import List, Optional, Any
from .base import BaseVectorStore, Document
import uuid
try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    Chroma = None

class ChromaVectorStore(BaseVectorStore):
    def __init__(self, collection_name: str = "datagent", persist_directory: Optional[str] = None):
        self.collection_name = collection_name
        if Chroma is None:
            raise ImportError("langchain-community is required for ChromaVectorStore")
            
        # We don't provide an embedding function here because we'll search by vector
        # or we rely on the caller to provide embeddings.
        # However, LangChain Chroma might warn if no embedding function is provided.
        self.vectorstore = Chroma(
            collection_name=collection_name,
            persist_directory=persist_directory,
            embedding_function=None 
        )

    async def add_documents(self, documents: List[Document]) -> List[str]:
        texts = [doc.content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [doc.id or str(uuid.uuid4()) for doc in documents]
        embeddings = [doc.embedding for doc in documents] if documents and documents[0].embedding else None

        # If embeddings are provided, use add_embeddings (if available) or add_texts with embeddings
        # LangChain Chroma add_texts supports 'embeddings' parameter?
        # Yes, it does (List[List[float]]).
        
        if embeddings and None not in embeddings:
             self.vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids, embeddings=embeddings)
        else:
            # If no embeddings, we can't add to Chroma without an embedding function unless we compute them.
            # But this class doesn't have the embedder.
            # So we assume embeddings are provided or we fail/warn.
            # Or we just add texts and hope Chroma has a default? No, default is SentenceTransformer usually but we passed None.
            raise ValueError("Documents must have embeddings when adding to ChromaVectorStore without an internal embedder.")
            
        return ids

    async def search(self, query_embedding: List[float], k: int = 4) -> List[Document]:
        results = self.vectorstore.similarity_search_by_vector(embedding=query_embedding, k=k)
        # Convert LangChain Documents back to our Document
        return [
            Document(
                content=res.page_content,
                metadata=res.metadata,
                id=res.metadata.get("id") # ID might be lost if not stored in metadata
            )
            for res in results
        ]
