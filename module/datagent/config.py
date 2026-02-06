from typing import Any, Dict
import yaml
import os
from .settings import settings

class ConfigLoader:
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Loads configuration from YAML and merges with Environment Variables."""
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f)
        
        # Merge with settings
        self.config["env"] = settings.ENV
        self.config["debug"] = settings.DEBUG
        
        return self.config

def load_config(path: str = None) -> Dict[str, Any]:
    return ConfigLoader(path).load()
