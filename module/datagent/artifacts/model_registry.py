from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ModelVersion:
    version: str
    uri: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class ModelRegistry:
    def __init__(self):
        self.models: Dict[str, Dict[str, ModelVersion]] = {}

    def register_model(self, name: str, uri: str, metadata: Optional[Dict[str, Any]] = None) -> ModelVersion:
        if name not in self.models:
            self.models[name] = {}
        
        version = str(len(self.models[name]) + 1)
        model_version = ModelVersion(version=version, uri=uri, metadata=metadata or {})
        self.models[name][version] = model_version
        return model_version

    def get_model(self, name: str, version: str) -> Optional[ModelVersion]:
        return self.models.get(name, {}).get(version)
