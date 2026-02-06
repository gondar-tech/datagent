import os
import shutil

class ArtifactStore:
    def __init__(self, base_path: str = "./artifacts"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def log_artifact(self, local_path: str, artifact_path: str) -> str:
        dest_path = os.path.join(self.base_path, artifact_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(local_path, dest_path)
        return dest_path

    def download_artifact(self, artifact_path: str, local_path: str):
        src_path = os.path.join(self.base_path, artifact_path)
        shutil.copy2(src_path, local_path)
