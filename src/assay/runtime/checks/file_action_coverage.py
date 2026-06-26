"""C3 — file-action-coverage check (port of ``checks/file-action-coverage.ts``)."""

from __future__ import annotations

from typing import Any

from ...config.defaults import HARDCODED_DEFAULTS
from ..id_generator import IdGenerator
from ..progress.file_action import (
    all_files_na,
    collect_declared_files,
    compute_file_action_progress,
)
from ..progress.impl_step import is_check_imp_step_complete
from ..progress.neutral import neutral_progress
from ..types.config import FileActionCoverageConfig, SeverityOverride
from ..types.context import (
    AssayContext,
    ExpectedAction,
    FileChangeStatus,
    JustificationApproved,
    WorkSessionFileChange,
)
from ..types.finding import Finding
from ..types.progress import CheckProgress
from .types import CheckOutput, CheckRunOptions, make_finding

# 'error' | 'warn' | 'silent'
SeverityOrSilent = str


def _downgrade_pending(severity: SeverityOverride) -> SeverityOrSilent:
    if severity == "off":
        return "silent"
    if severity == "error":
        return "warn"
    return severity


def _as_severity(value: SeverityOverride) -> SeverityOrSilent:
    return "silent" if value == "off" else value


def get_file_action_severity(
    status: FileChangeStatus,
    has_justification: bool,
    approved: JustificationApproved,
    is_impl_complete: bool,
    config: FileActionCoverageConfig | None = None,
    consider_justification_rejection: bool = False,
) -> SeverityOrSilent:
    if config is None:
        config = HARDCODED_DEFAULTS["checks"]["file-action-coverage"]
    if status == "matched":
        return "silent"

    just_state: str = approved if has_justification else "absent"

    if just_state == "approved":
        return "silent"
    if just_state == "pending":
        return _as_severity(config["pendingJustificationSeverity"])
    if just_state == "rejected":
        if not consider_justification_rejection:
            return "silent"
        return _as_severity(config["rejectedJustificationSeverity"])
    # 'absent'
    return _as_severity(config["severity"]) if is_impl_complete else _downgrade_pending(config["severity"])


def _compose_file_action_message(status: FileChangeStatus, expected_path: str) -> str:
    return {
        "missing": f"Expected file change not recorded: {expected_path}",
        "mismatched": f"File change did not match declared action: {expected_path}",
        "extra": f"Unexpected file change recorded: {expected_path}",
        "matched": f"File change matched: {expected_path}",
    }[status]


def _build_finding(
    *,
    ticket_id: str,
    expected_path: str,
    expected_action: ExpectedAction,
    status: FileChangeStatus,
    file_change: WorkSessionFileChange | None,
    severity: SeverityOrSilent,
    progress: CheckProgress,
    is_impl_complete: bool | None = None,
) -> dict[str, Any] | None:
    if severity == "silent":
        return None

    message = _compose_file_action_message(status, expected_path)
    fc = file_change
    ctx: dict[str, Any] = {
        "expectedPath": expected_path,
        "expectedAction": expected_action,
        "status": status,
        "progressTotal": progress.total,
        "progressCompleted": progress.completed,
        "progressRemaining": progress.remaining,
        "isImplComplete": is_impl_complete if is_impl_complete is not None else True,
    }
    if fc is not None:
        ctx["fileChangeId"] = fc.id
        # ctx.actualAction = fc.actualAction — undefined keys are dropped by JSON.stringify,
        # so omit the key entirely when the source value is absent (None).
        if fc.actual_action is not None:
            ctx["actualAction"] = fc.actual_action
        ctx["hasJustification"] = bool(fc.justification)
        ctx["justificationApproved"] = fc.justification_approved
    else:
        ctx["hasJustification"] = False

    entity_ids = [ticket_id, expected_path]
    if fc is not None:
        entity_ids.append(fc.id)

    return {
        "check_type": "file-action-coverage",
        "severity": severity,
        "message": message,
        "primary_entity_id": fc.id if fc is not None else expected_path,
        "entity_ids": entity_ids,
        "context": ctx,
    }


def _evaluate_file_change(
    ticket_id: str,
    fc: WorkSessionFileChange,
    status: FileChangeStatus,
    is_impl_complete: bool,
    progress: CheckProgress,
    cfg: FileActionCoverageConfig,
    consider_justification_rejection: bool,
) -> dict[str, Any] | None:
    has_justification = bool(fc.justification)
    approved = fc.justification_approved
    severity = get_file_action_severity(
        status,
        has_justification,
        approved,
        is_impl_complete,
        cfg,
        consider_justification_rejection,
    )
    return _build_finding(
        ticket_id=ticket_id,
        expected_path=fc.expected_path,
        expected_action=fc.expected_action,
        status=status,
        file_change=fc,
        severity=severity,
        progress=progress,
        is_impl_complete=is_impl_complete,
    )


def file_action_coverage_check(
    context: AssayContext,
    generate_id: IdGenerator,
    options: CheckRunOptions | None = None,
) -> CheckOutput:
    ticket = context.ticket
    file_changes = context.file_changes

    if all_files_na(ticket):
        return CheckOutput(findings=[], progress=neutral_progress())

    config = options.config if options is not None else HARDCODED_DEFAULTS
    consider = options.consider_justification_rejection if options is not None else False
    cfg: FileActionCoverageConfig = config["checks"]["file-action-coverage"]

    progress = compute_file_action_progress(context)
    findings: list[Finding] = []
    is_impl_complete = is_check_imp_step_complete(context)

    declared = collect_declared_files(ticket)
    matched_fc_ids: set[str] = set()

    for d in declared:
        fc = next(
            (
                x
                for x in file_changes
                if x.expected_path == d.expected_path and x.expected_action == d.expected_action
            ),
            None,
        )

        if fc is None:
            partial = _build_finding(
                ticket_id=ticket.id,
                expected_path=d.expected_path,
                expected_action=d.expected_action,
                status="missing",
                file_change=None,
                severity=get_file_action_severity(
                    "missing", False, "pending", is_impl_complete, cfg, consider
                ),
                progress=progress,
                is_impl_complete=is_impl_complete,
            )
            if partial is not None:
                findings.append(make_finding(generate_id, **partial))
            continue

        matched_fc_ids.add(fc.id)
        partial = _evaluate_file_change(
            ticket.id, fc, fc.status, is_impl_complete, progress, cfg, consider
        )
        if partial is not None:
            findings.append(make_finding(generate_id, **partial))

    for fc in file_changes:
        if fc.status != "extra":
            continue
        if fc.id in matched_fc_ids:
            continue
        matched_fc_ids.add(fc.id)
        partial = _evaluate_file_change(
            ticket.id, fc, fc.status, is_impl_complete, progress, cfg, consider
        )
        if partial is not None:
            findings.append(make_finding(generate_id, **partial))

    for fc in file_changes:
        if fc.id in matched_fc_ids:
            continue
        if fc.status == "extra":
            continue
        context_dict: dict[str, Any] = {
            "issue": "data-integrity",
            "expectedPath": fc.expected_path,
            "expectedAction": fc.expected_action,
            "status": fc.status,
        }
        findings.append(
            make_finding(
                generate_id,
                check_type="file-action-coverage",
                severity="error",
                message=(
                    "Data integrity: file change has no matching declared expectation: "
                    f"{fc.expected_path}"
                ),
                primary_entity_id=fc.id,
                entity_ids=[ticket.id, fc.id],
                context=context_dict,
            )
        )

    return CheckOutput(findings=findings, progress=progress)
