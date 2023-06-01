from typing import Any, Dict, List, Union
from .helpers import create_uuid
from src.github.models import CheckConclusionState, CheckSuite, CheckRun
from .builder_base_class import BuilderBaseClass
from .check_run_builder import CheckRunBuilder


class CheckSuiteBuilder(BuilderBaseClass):
    def __init__(self, conclusion=CheckConclusionState.NONE):
        self.raw_check_suite = {
            "node_id": create_uuid(),
            "checkRuns": [],
            "conclusion": conclusion,
        }

    def conclusion(self, conclusion: str) -> Union["CheckSuiteBuilder", CheckSuite]:
        self.raw_check_suite["conclusion"] = conclusion
        return self

    def check_runs(
        self, check_runs: List[Union[CheckRunBuilder, CheckRun]]
    ) -> Union["CheckSuiteBuilder", CheckSuite]:
        for check_run in check_runs:
            self.raw_check_suite["checkRuns"].append(check_run.to_raw())
        return self

    def build(self) -> CheckSuite:
        return CheckSuite(self.raw_check_suite)

    def to_raw(self) -> Dict[str, Any]:
        return self.build().to_raw()