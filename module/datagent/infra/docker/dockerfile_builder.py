from typing import List, Optional

class DockerfileBuilder:
    def __init__(self, base_image: str = "python:3.9-slim"):
        self.base_image = base_image
        self.steps = []

    def install_apt_packages(self, packages: List[str]):
        if packages:
            self.steps.append(f"RUN apt-get update && apt-get install -y {' '.join(packages)}")

    def install_pip_packages(self, packages: List[str]):
        if packages:
            self.steps.append(f"RUN pip install {' '.join(packages)}")

    def copy_file(self, src: str, dest: str):
        self.steps.append(f"COPY {src} {dest}")

    def set_cmd(self, cmd: List[str]):
        cmd_str = ", ".join([f'"{c}"' for c in cmd])
        self.steps.append(f"CMD [{cmd_str}]")

    def build(self) -> str:
        return f"FROM {self.base_image}\n" + "\n".join(self.steps)
