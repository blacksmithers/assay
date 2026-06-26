"""Acceptance-coverage finding templates (port of ``findings/acceptance-coverage.ts``)."""

from __future__ import annotations

from typing import Any

from .template_types import FindingTemplate

_COMPACT = """Acceptance criterion #{order} not verified.
 - GIVEN/WHEN/THEN as declared

 Verify the implemented behavior, then run mark_acceptance_check."""

_VERBOSE = """Acceptance criterion has not been verified yet.
 - Position: {order} of {progressTotal}
 - Progress: {progressCompleted} verified, {progressRemaining} remaining
 - GIVEN: {given}
 - WHEN: {when}
 - THEN: {then}

 An acceptance criterion is the contract between the spec and the implementation.
 Until you confirm the implemented behavior matches all GIVEN/WHEN/THEN clauses,
 the work session cannot complete.

 Possible reasons this is pending:
 - You implemented the behavior but have not run mark_acceptance_check yet
 - You haven't verified the behavior in this work session
 - The criterion describes behavior outside this ticket's scope

 Recommended moves:
 1. Verify the implemented behavior against the GIVEN/WHEN/THEN clauses above
 2. Run mark_acceptance_check with checked=true once verified
 3. If the criterion no longer applies, reopen the planning session to remove it from the spec — assayforge does not bypass declared ACs"""


def acceptance_coverage_dispatcher(_ctx: dict[str, Any]) -> FindingTemplate:
    return {
        "compact": _COMPACT,
        "verbose": _VERBOSE,
        "operations": ["mark_acceptance_check"],
    }
