"""Top-level result contracts (port of ``runtime/types/assay-result.ts``)."""

from __future__ import annotations

from typing import Any, Literal

from ._base import CamelModel
from .check_result import CheckResult
from .finding import Finding

AssayMode = Literal["action", "check"]


class AssayResultMeta(CamelModel):
    engine_version: str
    generated_at: str
    config_hash: str


class CheckModeSummary(CamelModel):
    message: str
    pending_by_action: dict[str, int]
    total_pending: int
    blocking_issues: int


class AssayChecks(CamelModel):
    acceptance_coverage: CheckResult
    implementation_coverage: CheckResult
    file_action_coverage: CheckResult
    test_result_presence: CheckResult


class AssayResult(CamelModel):
    passed: bool
    mode: AssayMode
    checks: AssayChecks
    findings: list[Finding]
    next_step: dict[str, Any] | None = None
    summary: CheckModeSummary | None = None
    meta: AssayResultMeta
