"""Implementation-step progress (port of ``progress/impl-step.ts``)."""

from __future__ import annotations

from ..field_declarations import is_field_na
from ..types.context import AssayContext
from ..types.progress import CheckProgress
from .neutral import neutral_progress


def compute_impl_step_progress(context: AssayContext) -> CheckProgress:
    ticket = context.ticket
    completions = context.impl_step_completions
    if is_field_na(ticket, "implementationSteps") or len(ticket.implementation_steps) == 0:
        return neutral_progress()

    done = {c.step_id for c in completions if c.done is True}

    ordered = sorted(ticket.implementation_steps, key=lambda s: s.order)
    remaining_ids: list[str] = []
    completed = 0
    for step in ordered:
        if step.id in done:
            completed += 1
        else:
            remaining_ids.append(step.id)

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


def is_check_imp_step_complete(context: AssayContext) -> bool:
    ticket = context.ticket
    if is_field_na(ticket, "implementationSteps"):
        return True
    if len(ticket.implementation_steps) == 0:
        return True
    done = {c.step_id for c in context.impl_step_completions if c.done is True}
    return all(s.id in done for s in ticket.implementation_steps)
