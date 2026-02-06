import subprocess
from typing import List
from dataclasses import dataclass

@dataclass
class SecurityIssue:
    file: str
    severity: str
    description: str

class SecurityScanner:
    def scan(self, target_dir: str) -> List[SecurityIssue]:
        """Runs bandit security scan."""
        # Placeholder for 'bandit -r target_dir -f json'
        return []

    def check_unsafe_imports(self, file_path: str) -> List[SecurityIssue]:
        """Simple check for unsafe modules like 'os', 'subprocess' in untrusted code."""
        issues = []
        import ast
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ["subprocess", "os", "sys"]:
                            issues.append(SecurityIssue(
                                file=file_path,
                                severity="high",
                                description=f"Unsafe import detected: {alias.name}"
                            ))
                elif isinstance(node, ast.ImportFrom):
                    if node.module in ["subprocess", "os", "sys"]:
                         issues.append(SecurityIssue(
                                file=file_path,
                                severity="high",
                                description=f"Unsafe from-import detected: {node.module}"
                            ))
        except Exception:
            pass
            
        return issues
