from typing import List, Dict
import asyncio

class GitHubCrawler:
    def __init__(self, token: str = None):
        self.token = token

    async def crawl(self, repo_url: str, branch: str = "main") -> List[Dict[str, str]]:
        """
        Crawls a GitHub repository and returns a list of files.
        Returns: List of dicts with keys 'path', 'content', 'url'.
        """
        # Mock implementation
        # In real world, use PyGithub or aiohttp to fetch tree and blobs
        return [
            {"path": "README.md", "content": "# Datagent", "url": f"{repo_url}/blob/{branch}/README.md"},
            {"path": "src/main.py", "content": "print('hello')", "url": f"{repo_url}/blob/{branch}/src/main.py"},
        ]
