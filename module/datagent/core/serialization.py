import dataclasses
from datetime import datetime
from typing import Any, Dict, Type, Set
import logging

from datagent.agents.schemas import BaseMessage

logger = logging.getLogger(__name__)

def get_all_subclasses(cls) -> Set[Type]:
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in get_all_subclasses(c)])

def _build_registry() -> Dict[str, Type]:
    registry = {}
    # Add all BaseMessage subclasses
    # We assume all relevant message types inherit from BaseMessage
    for cls in get_all_subclasses(BaseMessage):
        registry[cls.__name__] = cls
    return registry

def serialize(obj: Any) -> Any:
    """
    Recursively serialize objects to JSON-compatible types.
    Handles dataclasses and datetime objects.
    """
    if dataclasses.is_dataclass(obj):
        # Convert dataclass to dict
        d = {k: serialize(v) for k, v in dataclasses.asdict(obj).items()}
        # Inject type information for reconstruction
        d["_type"] = obj.__class__.__name__
        return d
    
    if isinstance(obj, datetime):
        return obj.isoformat()
        
    if isinstance(obj, list):
        return [serialize(x) for x in obj]
        
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
        
    return obj

def deserialize(obj: Any) -> Any:
    """
    Recursively deserialize JSON-compatible types back to objects.
    Reconstructs dataclasses using the _type field.
    """
    if isinstance(obj, list):
        return [deserialize(x) for x in obj]
        
    if isinstance(obj, dict):
        # Check if it's a serialized object
        if "_type" in obj:
            type_name = obj.pop("_type")
            registry = _build_registry()
            cls = registry.get(type_name)
            
            if cls:
                # Recursively deserialize fields
                kwargs = {k: deserialize(v) for k, v in obj.items()}
                
                # Special handling for timestamp (common in BaseMessage)
                if "timestamp" in kwargs and isinstance(kwargs["timestamp"], str):
                    try:
                        kwargs["timestamp"] = datetime.fromisoformat(kwargs["timestamp"])
                    except ValueError:
                        pass
                        
                try:
                    return cls(**kwargs)
                except Exception as e:
                    logger.warning(f"Failed to instantiate {type_name}: {e}")
                    # Fallback to dict
                    kwargs["_type"] = type_name
                    return kwargs
            else:
                # Class not found in registry
                logger.warning(f"Class {type_name} not found in registry. Returning dict.")
                obj["_type"] = type_name # restore type
                return {k: deserialize(v) for k, v in obj.items()}
                
        return {k: deserialize(v) for k, v in obj.items()}
        
    return obj
