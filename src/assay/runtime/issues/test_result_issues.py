"""Open test-result issue detection (port of ``issues/test-result-issues.ts``).

Supersede semantics: a later passing run for the same ``(testType, command)``
supersedes any older run for that pair.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..types.context import AssayContext, WorkSessionTestResult
from ..types.issues import TestResultIssue


@dataclass
class TestResultIssueEntry:
    test_result: WorkSessionTestResult
    issue: TestResultIssue


def _key(tr: WorkSessionTestResult) -> str:
    return f"{tr.test_type}|{tr.command or ''}"


def find_open_test_result_issues(
    context: AssayContext,
    # Reserved for future flag-true detection of failure/skip rejection states.
    _consider_justification_rejection: bool,
) -> list[TestResultIssueEntry]:
    issues: list[TestResultIssueEntry] = []

    # Step 1 — supersede map: latest passing run per (testType, command).
    latest_passing_run_at: dict[str, str] = {}
    for tr in context.test_results:
        if not tr.all_passed:
            continue
        k = _key(tr)
        current = latest_passing_run_at.get(k)
        if current is None or tr.run_at > current:
            latest_passing_run_at[k] = tr.run_at

    # Step 2 — walk results, skipping superseded ones.
    for tr in context.test_results:
        superseded_by = latest_passing_run_at.get(_key(tr))
        if superseded_by is not None and tr.run_at < superseded_by:
            continue

        if tr.skipped > 0 and len(tr.skipped_justifications) == 0:
            issues.append(TestResultIssueEntry(tr, "skipped-without-justification"))

        if (not tr.all_passed) and tr.failed > 0 and len(tr.failure_justifications) == 0:
            issues.append(TestResultIssueEntry(tr, "tests-failing"))

        # Rejection states are reserved for future M5 wiring.

    issues.sort(key=lambda e: e.test_result.run_at)
    return issues
