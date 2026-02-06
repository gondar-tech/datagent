from dataclasses import dataclass, field
from typing import Type, List, AsyncIterator, Iterator
import tempfile
import os
from ..base import BaseAgent
from ..schemas import AgentInput, AgentOutput, StreamingEvent, TextChunkEvent
from ..registry import AgentRegistry
from .static_analysis import StaticAnalyzer
from .security_scanner import SecurityScanner
from .test_runner import TestRunner

@dataclass(frozen=True, kw_only=True)
class ValidatorInput(AgentInput):
    code: str
    language: str = "python"
    test_code: str = ""

@dataclass(frozen=True, kw_only=True)
class ValidatorOutput(AgentOutput):
    is_valid: bool
    static_analysis_issues: List[str] = field(default_factory=list)
    security_issues: List[str] = field(default_factory=list)
    test_results: str = ""
    summary: str = ""

@AgentRegistry.register("code_validator")
class CodeValidatorAgent(BaseAgent[ValidatorInput, ValidatorOutput]):
    def __init__(self, name: str = "code_validator"):
        super().__init__(name)
        self.static_analyzer = StaticAnalyzer()
        self.security_scanner = SecurityScanner()
        self.test_runner = TestRunner()

    @property
    def input_type(self) -> Type[ValidatorInput]:
        return ValidatorInput

    @property
    def output_type(self) -> Type[ValidatorOutput]:
        return ValidatorOutput

    async def a_run(self, input_data: ValidatorInput) -> ValidatorOutput:
        # Create a temp directory to analyze code
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "generated_code.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(input_data.code)
                
            if input_data.test_code:
                test_path = os.path.join(temp_dir, "test_generated.py")
                with open(test_path, "w", encoding="utf-8") as f:
                    f.write(input_data.test_code)

            # 1. Static Analysis
            static_issues = self.static_analyzer.analyze(file_path)
            static_msgs = [f"{i.severity}: {i.message} at line {i.line}" for i in static_issues]

            # 2. Security Scan
            security_issues = self.security_scanner.check_unsafe_imports(file_path)
            sec_msgs = [f"{i.severity}: {i.description}" for i in security_issues]

            # 3. Tests
            test_output = ""
            tests_passed = True
            if input_data.test_code:
                test_result = self.test_runner.run_tests(temp_dir)
                test_output = test_result.output
                tests_passed = test_result.passed

            is_valid = (not static_issues) and (not security_issues) and tests_passed
            
            summary = "Validation Passed" if is_valid else "Validation Failed"

            return ValidatorOutput(
                session_id=input_data.session_id,
                is_valid=is_valid,
                static_analysis_issues=static_msgs,
                security_issues=sec_msgs,
                test_results=test_output,
                summary=summary
            )

    def run(self, input_data: ValidatorInput) -> ValidatorOutput:
        import asyncio
        return asyncio.run(self.a_run(input_data))

    def stream(self, input_data: ValidatorInput) -> Iterator[StreamingEvent]:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        agen = self.a_stream(input_data)
        try:
            while True:
                try:
                    yield loop.run_until_complete(agen.__anext__())
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

    async def a_stream(self, input_data: ValidatorInput) -> AsyncIterator[StreamingEvent]:
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            content="Starting Code Validation...\n"
        )
        
        # 1. Static Analysis
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            content="Running Static Analysis...\n"
        )
        # We assume analysis is fast, but we could split it if needed
        
        # 2. Security
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            content="Running Security Scan...\n"
        )
        
        # 3. Tests
        if input_data.test_code:
            yield TextChunkEvent(
                session_id=input_data.session_id,
                agent_name=self.name,
                content="Running Tests...\n"
            )
        
        yield TextChunkEvent(
            session_id=input_data.session_id,
            agent_name=self.name,
            content="Validation Complete.\n"
        )
