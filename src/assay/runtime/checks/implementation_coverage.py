"""C2 — implementation-coverage check (port of ``checks/implementation-coverage.ts``)."""

from __future__ import annotations

from ...config.defaults import HARDCODED_DEFAULTS
from ..field_declarations import is_field_na
from ..id_generator import IdGenerator
from ..progress.impl_step import compute_impl_step_progress
from ..progress.neutral import neutral_progress
from ..types.context import AssayContext
from ..types.finding import Finding
from .types import CheckOutput, CheckRunOptions, make_finding


def implementation_coverage_check(
    context: AssayContext,
    generate_id: IdGenerator,
    options: CheckRunOptions | None = None,
) -> CheckOutput:
    ticket = context.ticket
    impl_step_completions = context.impl_step_completions

    if is_field_na(ticket, "implementationSteps") or len(ticket.implementation_steps) == 0:
        return CheckOutput(findings=[], progress=neutral_progress())

    config = options.config if options is not None else HARDCODED_DEFAULTS
    cfg = config["checks"]["implementation-coverage"]

    progress = compute_impl_step_progress(context)
    if cfg["severity"] == "off":
        return CheckOutput(findings=[], progress=progress)
    severity = cfg["severity"]

    done = {c.step_id for c in impl_step_completions if c.done is True}

    ordered = sorted(ticket.implementation_steps, key=lambda s: s.order)
    findings: list[Finding] = []

    for step in ordered:
        if step.id in done:
            continue
        context_dict = {
            "text": step.text,
            "order": step.order,
            "progressTotal": progress.total,
            "progressCompleted": progress.completed,
            "progressRemaining": progress.remaining,
        }
        findings.append(
            make_finding(
                generate_id,
                check_type="implementation-coverage",
                severity=severity,
                message=f"Implementation step not completed: {step.id}",
                primary_entity_id=step.id,
                entity_ids=[ticket.id, step.id],
                context=context_dict,
            )
        )

    return CheckOutput(findings=findings, progress=progress)
