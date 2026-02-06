from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class ExperimentTracker(ABC):
    @abstractmethod
    def log_param(self, key: str, value: Any):
        pass

    @abstractmethod
    def log_metric(self, key: str, value: float, step: Optional[int] = None):
        pass

    @abstractmethod
    def log_artifact(self, local_path: str):
        pass

class SimpleTracker(ExperimentTracker):
    def __init__(self):
        self.params = {}
        self.metrics = []
        self.artifacts = []

    def log_param(self, key: str, value: Any):
        self.params[key] = value

    def log_metric(self, key: str, value: float, step: Optional[int] = None):
        self.metrics.append({"key": key, "value": value, "step": step})

    def log_artifact(self, local_path: str):
        self.artifacts.append(local_path)
