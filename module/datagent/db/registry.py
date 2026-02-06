from typing import Dict, Type
from .repositories.base import BaseRepository

class RepositoryRegistry:
    _registry: Dict[str, Type[BaseRepository]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(repo_cls: Type[BaseRepository]):
            cls._registry[name] = repo_cls
            return repo_cls
        return decorator

    @classmethod
    def get(cls, name: str) -> Type[BaseRepository]:
        if name not in cls._registry:
            raise ValueError(f"Repository {name} not found")
        return cls._registry[name]
