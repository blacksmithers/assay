"""Test-result progress (port of ``progress/test-result.ts``)."""

from __future__ import annotations

from ..field_declarations import is_field_na
from ..types.context import AssayContext
from ..types.progress import CheckProgress
from .neutral import neutral_progress


def compute_test_result_progress(context: AssayContext) -> CheckProgress:
    ticket = context.ticket
    test_results = context.test_results
    if is_field_na(ticket, "testSpecification"):
        return neutral_progress()
    spec = ticket.test_specification
    if spec is None or len(spec.test_types) == 0:
        return neutral_progress()

    remaining_ids: list[str] = []
    completed = 0
    for test_type in spec.test_types:
        results = [r for r in test_results if r.test_type == test_type]
        has_passing = any(r.all_passed is True for r in results)
        has_justified_skip = any(
            r.skipped > 0 and len(r.skipped_justifications) > 0 for r in results
        )
        if has_passing or has_justified_skip:
            completed += 1
        else:
            remaining_ids.append(test_type)

    total = len(spec.test_types)
    remaining = total - completed
    return CheckProgress(
        total=total, completed=completed, remaining=remaining, remaining_ids=remaining_ids
    )
