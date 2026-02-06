from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

class StateManager(ABC):
    @abstractmethod
    async def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def set_state(self, key: str, value: Dict[str, Any]):
        pass

class InMemoryStateManager(StateManager):
    def __init__(self):
        self._state = {}

    async def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        return self._state.get(key)

    async def set_state(self, key: str, value: Dict[str, Any]):
        self._state[key] = value
