from typing import Dict, List
import os

class MultiFileBuilder:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path

    def build(self, files: Dict[str, str]):
        """
        Writes a dictionary of filename -> content to disk.
        """
        for filename, content in files.items():
            path = os.path.join(self.base_path, filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
                
    def preview(self, files: Dict[str, str]) -> str:
        """Returns a string representation of the file structure."""
        output = []
        for filename, content in files.items():
            output.append(f"--- {filename} ---")
            output.append(content)
            output.append("--- End of File ---\n")
        return "\n".join(output)
