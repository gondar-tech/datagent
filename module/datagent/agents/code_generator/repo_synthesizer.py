from typing import Dict, List
from dataclasses import dataclass
from .multi_file_builder import MultiFileBuilder

@dataclass
class RepoStructure:
    files: Dict[str, str]
    dependencies: List[str]

class RepoSynthesizer:
    def __init__(self, builder: MultiFileBuilder):
        self.builder = builder

    def synthesize(self, structure: RepoStructure, base_path: str = "."):
        """
        Takes a dictionary of files and writes them to disk using the builder.
        Also handles dependency files (requirements.txt).
        """
        # 1. Add normal files
        for path, content in structure.files.items():
            self.builder.add_file(path, content)

        # 2. Add requirements.txt if dependencies exist
        if structure.dependencies:
            req_content = "\n".join(structure.dependencies)
            self.builder.add_file("requirements.txt", req_content)

        # 3. Build
        self.builder.build(base_path)
