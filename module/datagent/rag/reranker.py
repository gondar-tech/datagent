from typing import List, Dict, Any

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        # self.model = CrossEncoder(model_name)

    def rerank(self, query: str, docs: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Reranks a list of documents based on relevance to the query.
        """
        # Mock implementation since we don't have sentence-transformers installed
        # In real world: scores = self.model.predict([(query, doc['content']) for doc in docs])
        
        # Just return top_k of the original list for now
        return docs[:top_k]
