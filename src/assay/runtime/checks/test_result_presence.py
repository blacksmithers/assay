"""C4 — test-result-presence check (port of ``checks/test-result-presence.ts``)."""

from __future__ import annotations

from typing import Any

from ...config.defaults import HARDCODED_DEFAULTS
from ..field_declarations import is_field_na
from ..id_generator import IdGenerator
from ..progress.neutral import neutral_progress
from ..progress.test_result import compute_test_result_progress
from ..types.config import SeverityOverride
from ..types.context import AssayContext
from ..types.finding import Finding, FindingSeverity
from .types import CheckOutput, CheckRunOptions, make_finding


def _as_severity(value: SeverityOverride) -> FindingSeverity | None:
    return None if value == "off" else value


def test_result_presence_check(
    context: AssayContext,
    generate_id: IdGenerator,
    options: CheckRunOptions | None = None,
) -> CheckOutput:
    ticket = context.ticket
    test_results = context.test_results

    if is_field_na(ticket, "testSpecification"):
        return CheckOutput(findings=[], progress=neutral_progress())
    spec = ticket.test_specification
    if spec is None or len(spec.test_types) == 0:
        return CheckOutput(findings=[], progress=neutral_progress())

    config = options.config if options is not None else HARDCODED_DEFAULTS
    cfg = config["checks"]["test-result-presence"]

    progress = compute_test_result_progress(context)
    findings: list[Finding] = []

    coverage_severity = _as_severity(cfg["severity"])
    if coverage_severity is not None:
        for test_type in spec.test_types:
            results = [r for r in test_results if r.test_type == test_type]
            has_passing = any(r.all_passed is True for r in results)
            has_justified_skip = any(
                r.skipped > 0 and len(r.skipped_justifications) > 0 for r in results
            )
            if not has_passing and not has_justified_skip:
                ctx: dict[str, Any] = {
                    "issue": "missing-coverage",
                    "testType": test_type,
                    "progressTotal": progress.total,
                    "progressCompleted": progress.completed,
                    "progressRemaining": progress.remaining,
                }
                findings.append(
                    make_finding(
                        generate_id,
                        check_type="test-result-presence",
                        severity=coverage_severity,
                        message=f"Test type not satisfied: {test_type}",
                        primary_entity_id=test_type,
                        entity_ids=[ticket.id],
                        context=ctx,
                    )
                )

    skipped_severity = _as_severity(cfg["skippedWithoutJustificationSeverity"])
    if skipped_severity is not None:
        for result in test_results:
            if result.skipped > 0 and len(result.skipped_justifications) == 0:
                ctx_s: dict[str, Any] = {
                    "issue": "skipped-without-justification",
                    "testType": result.test_type,
                    "skipped": result.skipped,
                }
                if result.command is not None:
                    ctx_s["command"] = result.command
                findings.append(
                    make_finding(
                        generate_id,
                        check_type="test-result-presence",
                        severity=skipped_severity,
                        message=f"Tests skipped without justification: {result.test_type}",
                        primary_entity_id=result.id,
                        entity_ids=[ticket.id, result.id],
                        context=ctx_s,
                    )
                )

    failing_severity = _as_severity(cfg["testsFailingSeverity"])
    if failing_severity is not None:
        for result in test_results:
            if result.all_passed is False:
                ctx_f: dict[str, Any] = {
                    "issue": "tests-failing",
                    "testType": result.test_type,
                    "failed": result.failed,
                    "passed": result.passed,
                    "total": result.total,
                }
                if result.command is not None:
                    ctx_f["command"] = result.command
                findings.append(
                    make_finding(
                        generate_id,
                        check_type="test-result-presence",
                        severity=failing_severity,
                        message=f"Tests failing: {result.test_type}",
                        primary_entity_id=result.id,
                        entity_ids=[ticket.id, result.id],
                        context=ctx_f,
                    )
                )

    return CheckOutput(findings=findings, progress=progress)
