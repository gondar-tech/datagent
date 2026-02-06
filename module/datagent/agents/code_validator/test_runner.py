import subprocess
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class TestResult:
    passed: bool
    output: str
    errors: List[str]

class TestRunner:
    def run_tests(self, test_dir: str) -> TestResult:
        """Runs pytest on the specified directory."""
        try:
            # Running pytest as a subprocess
            result = subprocess.run(
                ["pytest", test_dir],
                capture_output=True,
                text=True,
                timeout=60 # 1 minute timeout
            )
            
            passed = result.returncode == 0
            return TestResult(
                passed=passed,
                output=result.stdout,
                errors=[result.stderr] if result.stderr else []
            )
        except Exception as e:
            return TestResult(
                passed=False,
                output="",
                errors=[str(e)]
            )
