"""Per-check result contract (port of ``runtime/types/check-result.ts``)."""

from __future__ import annotations

from ._base import CamelModel
from .finding import AssayCheckType, Finding
from .progress import CheckProgress


class CheckResult(CamelModel):
    check_type: AssayCheckType
    passed: bool
    findings: list[Finding]
    progress: CheckProgress
