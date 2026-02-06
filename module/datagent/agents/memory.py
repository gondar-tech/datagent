from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class MemoryItem:
    role: str
    content: str
    timestamp: float

class BaseMemory(ABC):
    @abstractmethod
    def add(self, role: str, content: str):
        pass

    @abstractmethod
    def get_history(self) -> List[MemoryItem]:
        pass

class ShortTermMemory(BaseMemory):
    def __init__(self):
        self._items: List[MemoryItem] = []

    def add(self, role: str, content: str):
        import time
        self._items.append(MemoryItem(role, content, time.time()))

    def get_history(self) -> List[MemoryItem]:
        return self._items
