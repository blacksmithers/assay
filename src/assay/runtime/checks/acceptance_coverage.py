"""C1 — acceptance-coverage check (port of ``checks/acceptance-coverage.ts``)."""

from __future__ import annotations

from ...config.defaults import HARDCODED_DEFAULTS
from ..field_declarations import is_field_na
from ..id_generator import IdGenerator
from ..progress.acceptance import compute_acceptance_progress
from ..progress.neutral import neutral_progress
from ..types.context import AssayContext
from ..types.finding import Finding
from .types import CheckOutput, CheckRunOptions, make_finding


def acceptance_coverage_check(
    context: AssayContext,
    generate_id: IdGenerator,
    options: CheckRunOptions | None = None,
) -> CheckOutput:
    ticket = context.ticket
    acceptance_checks = context.acceptance_checks

    if is_field_na(ticket, "acceptanceCriteria") or len(ticket.acceptance_criteria) == 0:
        return CheckOutput(findings=[], progress=neutral_progress())

    config = options.config if options is not None else HARDCODED_DEFAULTS
    cfg = config["checks"]["acceptance-coverage"]

    progress = compute_acceptance_progress(context)
    if cfg["severity"] == "off":
        return CheckOutput(findings=[], progress=progress)
    severity = cfg["severity"]

    checked = {c.criterion_id for c in acceptance_checks if c.checked is True}

    ordered = sorted(ticket.acceptance_criteria, key=lambda a: a.order)
    findings: list[Finding] = []

    for ac in ordered:
        if ac.id in checked:
            continue
        context_dict = {
            "given": ac.given,
            "when": ac.when,
            "then": ac.then,
            "order": ac.order,
            "progressTotal": progress.total,
            "progressCompleted": progress.completed,
            "progressRemaining": progress.remaining,
        }
        findings.append(
            make_finding(
                generate_id,
                check_type="acceptance-coverage",
                severity=severity,
                message=f"Acceptance criterion not verified: {ac.id}",
                primary_entity_id=ac.id,
                entity_ids=[ticket.id, ac.id],
                context=context_dict,
            )
        )

    return CheckOutput(findings=findings, progress=progress)
