import hashlib
from typing import Any

class Versioning:
    @staticmethod
    def generate_hash(content: Any) -> str:
        """Generates a SHA256 hash for the given content."""
        if isinstance(content, str):
            data = content.encode("utf-8")
        else:
            data = str(content).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def increment_version(version: str) -> str:
        """Increments a semantic version string (e.g., '1.0.0' -> '1.0.1')."""
        parts = version.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid version format. Expected x.y.z")
        
        major, minor, patch = map(int, parts)
        return f"{major}.{minor}.{patch + 1}"
