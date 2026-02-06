from typing import Dict, Any

class MetadataExtractor:
    def extract(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Extracts metadata from file path and content.
        """
        return {
            "extension": file_path.split('.')[-1] if '.' in file_path else "",
            "language": self._detect_language(file_path),
            "size": len(content)
        }

    def _detect_language(self, path: str) -> str:
        if path.endswith(".py"): return "python"
        if path.endswith(".js"): return "javascript"
        if path.endswith(".md"): return "markdown"
        return "unknown"
