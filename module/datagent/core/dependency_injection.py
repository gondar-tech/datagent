from typing import Any, Dict, Type, TypeVar, Optional

T = TypeVar("T")

class Container:
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Any] = {}

    def register_instance(self, interface: Type[T], instance: T):
        self._services[interface] = instance

    def register_factory(self, interface: Type[T], factory: Any):
        self._factories[interface] = factory

    def resolve(self, interface: Type[T]) -> T:
        if interface in self._services:
            return self._services[interface]
        
        if interface in self._factories:
            instance = self._factories[interface]()
            # Singleton by default for factories? Let's keep it simple and just return new instance
            # or we could cache it.
            return instance
            
        raise ValueError(f"Service {interface} not registered")

# Global container instance
container = Container()
