"""Acceptance-criteria progress (port of ``progress/acceptance.ts``)."""

from __future__ import annotations

from ..field_declarations import is_field_na
from ..types.context import AssayContext
from ..types.progress import CheckProgress
from .neutral import neutral_progress


def compute_acceptance_progress(context: AssayContext) -> CheckProgress:
    ticket = context.ticket
    acceptance_checks = context.acceptance_checks
    if is_field_na(ticket, "acceptanceCriteria") or len(ticket.acceptance_criteria) == 0:
        return neutral_progress()

    checked = {c.criterion_id for c in acceptance_checks if c.checked is True}

    ordered = sorted(ticket.acceptance_criteria, key=lambda a: a.order)
    remaining_ids: list[str] = []
    completed = 0
    for ac in ordered:
        if ac.id in checked:
            completed += 1
        else:
            remaining_ids.append(ac.id)

    total = len(ordered)
    remaining = total - completed
    if remaining_ids:
        return CheckProgress(
            total=total,
            completed=completed,
            remaining=remaining,
            remaining_ids=remaining_ids,
            next_in_order_id=remaining_ids[0],
        )
    return CheckProgress(
        total=total, completed=completed, remaining=remaining, remaining_ids=remaining_ids
    )
