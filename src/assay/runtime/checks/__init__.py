"""Check registry (port of ``checks/index.ts``)."""

from __future__ import annotations

from ..types.finding import AssayCheckType
from .acceptance_coverage import acceptance_coverage_check
from .file_action_coverage import file_action_coverage_check, get_file_action_severity
from .implementation_coverage import implementation_coverage_check
from .test_result_presence import test_result_presence_check
from .types import CheckFn, CheckOutput, CheckRunOptions

CHECK_REGISTRY: dict[AssayCheckType, CheckFn] = {
    "acceptance-coverage": acceptance_coverage_check,
    "implementation-coverage": implementation_coverage_check,
    "file-action-coverage": file_action_coverage_check,
    "test-result-presence": test_result_presence_check,
}

__all__ = [
    "CHECK_REGISTRY",
    "CheckFn",
    "CheckOutput",
    "CheckRunOptions",
    "acceptance_coverage_check",
    "file_action_coverage_check",
    "get_file_action_severity",
    "implementation_coverage_check",
    "test_result_presence_check",
]
