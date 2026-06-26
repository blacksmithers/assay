"""Test-result-presence finding templates (port of ``findings/test-result-presence.ts``)."""

from __future__ import annotations

from typing import Any

from .template_types import FindingTemplate

# C4.1 — testType missing coverage
_C4_1_COMPACT = """Test type {testType} has no satisfying result.

 Run the tests and register via record_test_result, OR record skip with justification."""

_C4_1_VERBOSE = """A required test type has no recorded result.
 - Test type: {testType}
 - Recorded results for this type: {resultCount}

 The spec declares this test type as required for the ticket. No registered result
 satisfies it (either no run is recorded, or all recorded runs have allPassed=false
 without a passing retry).

 Possible reasons:
 - You haven't run the tests for this type yet
 - You ran the tests but did not register the result via record_test_result
 - All runs failed; you need to fix the failures and re-run, or justify the failure

 Recommended moves:
 1. Run the test command(s) for {testType} (typically present in ticket.testSpecification.testCommands)
 2. Register the outcome via record_test_result with the actual pass/fail/skip counts
 3. If the tests cannot pass and the failures are intentional, attach add_failure_justification
 4. If the tests must be skipped (e.g., environment unavailable), attach add_skip_justification"""

# C4.2 — skipped without justification
_C4_2_COMPACT = """Tests skipped without justification.
 - {testType}: {skipped}/{total} skipped

 Attach reasons via add_skip_justification."""

_C4_2_VERBOSE = """Tests were skipped without a justification.
 - Test type: {testType}
 - Skipped: {skipped} of {total}

 A test result was registered with skipped tests, but no justification entries
 were provided to explain why those tests were not executed. Skips without
 justification block work session completion — the spec assumes every relevant
 test ran, and skips need a reason.

 Possible reasons:
 - The tests were skipped due to environment limitations (e.g., flaky, requires deps)
 - The tests are obsolete and should be removed (consider reopening planning)
 - The skip was unintentional (the test runner skipped them without your awareness)

 Recommended moves:
 1. Inspect why the tests were skipped (test runner output, suite metadata)
 2. If the skips are legitimate, attach one justification entry per skipped test via add_skip_justification
 3. If the skips were unintentional, fix the test config and re-run; record the new result via record_test_result
 4. If the tests are obsolete, reopen the planning session to remove them from the test specification"""

# C4.3 — tests failing without justification
_C4_3_COMPACT = """Tests failing without justification.
 - {testType}: {failed}/{total} failed

 Fix and re-run (auto-supersedes), OR justify via add_failure_justification."""

_C4_3_VERBOSE = """Recorded test result has failures without a justification.
 - Test type: {testType}
 - Failed: {failed} of {total}

 The most recent recorded result for this test type has failed tests, and no
 failure justifications were provided. Failing tests without justification
 block work session completion. Note: a later passing run for the same
 (testType, command) supersedes this one — if you fix and re-run, this finding
 disappears.

 Possible reasons:
 - The tests legitimately fail and you haven't fixed them yet
 - The failures are known/intentional (e.g., known flaky test) and need justification
 - The implementation is incomplete and this is expected at this stage

 Recommended moves:
 1. Inspect the failures and determine root cause
 2. Fix the failing tests, re-run, and register the new passing result via record_test_result (the older failing entry remains as historical record)
 3. If the failures are intentional and acceptable, attach failure justifications via add_failure_justification
 4. If the implementation is incomplete, return to check-imp-step and complete pending steps"""

# C4.4 — failure justification rejected (gated)
_C4_4_COMPACT = """Justification rejected — review tests.
 - {testType}: {failed}/{total} failed

 Fix tests OR amend_failure_justification."""

_C4_4_VERBOSE = """Justification not accepted — review tests.
 - Test type: {testType}
 - Failed: {failed} of {total}
 - Approval state: rejected

 The failure justifications you provided were rejected. The reviewer wants
 either the tests to actually pass or a stronger justification for accepting failure.

 Possible reasons:
 - The reviewer wants the tests to pass; failure is not acceptable here
 - The justification did not adequately explain why failure is intentional
 - There may be a misunderstanding about what 'acceptable' means for this test type

 Recommended moves:
 1. Re-read the rejection context (typically passed alongside this finding)
 2. If failures should be fixed, fix the tests and re-run; register the passing result via record_test_result
 3. If the justification needs rework, run amend_failure_justification with stronger reasoning"""

# C4.5 — skip justification rejected (gated)
_C4_5_COMPACT = """Justification rejected — review skipped tests.
 - {testType}: {skipped}/{total} skipped

 Run the skipped tests OR amend_skip_justification."""

_C4_5_VERBOSE = """Justification not accepted — review skipped tests.
 - Test type: {testType}
 - Skipped: {skipped} of {total}
 - Approval state: rejected

 The skip justifications you provided were rejected. The reviewer wants either
 the tests to actually run or a stronger justification for skipping.

 Possible reasons:
 - The reviewer believes the skipped tests should run despite environment difficulty
 - The justification did not adequately explain why skips are necessary
 - The test config can be fixed to enable the tests in this environment

 Recommended moves:
 1. Re-read the rejection context
 2. If skips should be eliminated, fix the test config and re-run; register the new result
 3. If the justification needs rework, run amend_skip_justification with stronger reasoning"""

_T_4_1: FindingTemplate = {
    "compact": _C4_1_COMPACT,
    "verbose": _C4_1_VERBOSE,
    "operations": ["record_test_result", "add_skip_justification"],
}
_T_4_2: FindingTemplate = {
    "compact": _C4_2_COMPACT,
    "verbose": _C4_2_VERBOSE,
    "operations": ["record_test_result", "add_skip_justification"],
}
_T_4_3: FindingTemplate = {
    "compact": _C4_3_COMPACT,
    "verbose": _C4_3_VERBOSE,
    "operations": ["record_test_result", "add_failure_justification"],
}
_T_4_4: FindingTemplate = {
    "compact": _C4_4_COMPACT,
    "verbose": _C4_4_VERBOSE,
    "operations": ["record_test_result", "amend_failure_justification"],
}
_T_4_5: FindingTemplate = {
    "compact": _C4_5_COMPACT,
    "verbose": _C4_5_VERBOSE,
    "operations": ["record_test_result", "amend_skip_justification"],
}


def test_result_presence_dispatcher(ctx: dict[str, Any]) -> FindingTemplate:
    issue = ctx.get("issue")
    if issue == "missing-coverage":
        return _T_4_1
    if issue == "skipped-without-justification":
        return _T_4_2
    if issue == "tests-failing":
        return _T_4_3
    if issue == "failure-justification-rejected":
        return _T_4_4
    if issue == "skip-justification-rejected":
        return _T_4_5
    return _T_4_1
