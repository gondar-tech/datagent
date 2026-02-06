from typing import List
from .embedder import BaseEmbedder
from .vector_store.base import BaseVectorStore, Document
from .retriever import Retriever
from .github_indexer.crawler import GitHubCrawler
from .github_indexer.chunker import CodeChunker

class RAGPipeline:
    def __init__(
        self,
        embedder: BaseEmbedder,
        vector_store: BaseVectorStore,
        crawler: GitHubCrawler = None,
        chunker: CodeChunker = None
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.retriever = Retriever(vector_store, embedder)
        self.crawler = crawler or GitHubCrawler()
        self.chunker = chunker or CodeChunker()

    async def index_repository(self, repo_url: str):
        files = await self.crawler.crawl(repo_url)
        documents = []
        for file in files:
            chunks = self.chunker.chunk(file['content'])
            embeddings = await self.embedder.embed_documents(chunks)
            for i, chunk in enumerate(chunks):
                documents.append(Document(
                    content=chunk,
                    metadata={"source": file['url'], "path": file['path']},
                    embedding=embeddings[i]
                ))
        await self.vector_store.add_documents(documents)

    async def query(self, query_text: str, k: int = 4) -> List[Document]:
        return await self.retriever.retrieve(query_text, k)
