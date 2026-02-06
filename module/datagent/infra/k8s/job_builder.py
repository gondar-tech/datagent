from typing import Dict, Any, List

class K8sJobBuilder:
    def __init__(self, job_name: str, image: str):
        self.job_name = job_name
        self.image = image
        self.env_vars = {}
        self.command = []

    def set_env(self, key: str, value: str):
        self.env_vars[key] = value

    def set_command(self, command: List[str]):
        self.command = command

    def build(self) -> Dict[str, Any]:
        return {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {"name": self.job_name},
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": self.job_name,
                            "image": self.image,
                            "command": self.command,
                            "env": [{"name": k, "value": v} for k, v in self.env_vars.items()]
                        }],
                        "restartPolicy": "Never"
                    }
                }
            }
        }
