"""Next-step resolution (port of ``next-step/resolver.ts``).

The resolved next-step is a plain ordered ``dict`` mirroring the TS object
literal. Embedded input rows (``implStep``, ``acceptanceCriterion``,
``issues[].fileChange`` / ``.testResult``) carry their zod-faithful
serialization (via :meth:`InputModel.to_input_dict`); ``progress`` is rendered
to a plain dict; ``guidance`` starts as a placeholder and is filled by the
engine. Dict key order is immaterial — output is compared structurally.
"""

from __future__ import annotations

from typing import Any

from ..enums import AssayAction
from ..issues.file_change_issues import FileChangeIssueEntry, find_open_file_change_issues
from ..issues.test_result_issues import TestResultIssueEntry, find_open_test_result_issues
from ..progress.acceptance import compute_acceptance_progress
from ..progress.file_action import collect_declared_files, compute_file_action_progress
from ..progress.impl_step import compute_impl_step_progress
from ..progress.test_result import compute_test_result_progress
from ..types.context import AcceptanceCriterion, AssayContext, ImplementationStep
from ..types.options import AssayOptions
from ..types.progress import CheckProgress
from .applicability import applicable_actions


def _placeholder_guidance() -> dict[str, Any]:
    return {"message": "", "operations": []}


def _progress_to_dict(progress: CheckProgress) -> dict[str, Any]:
    out: dict[str, Any] = {
        "total": progress.total,
        "completed": progress.completed,
        "remaining": progress.remaining,
        "remainingIds": list(progress.remaining_ids),
    }
    if progress.next_in_order_id is not None:
        out["nextInOrderId"] = progress.next_in_order_id
    return out


def _progress_for(action: AssayAction, context: AssayContext) -> CheckProgress:
    if action == "check-imp-step":
        return compute_impl_step_progress(context)
    if action == "check-ac":
        return compute_acceptance_progress(context)
    if action == "add-files-changes":
        return compute_file_action_progress(context)
    return compute_test_result_progress(context)


def _find_issues_for(
    action: AssayAction,
    context: AssayContext,
    consider_justification_rejection: bool,
) -> dict[str, Any]:
    if action == "add-files-changes":
        fc = find_open_file_change_issues(context, consider_justification_rejection)
        return {"fileChange": fc, "count": len(fc)}
    if action == "add-test-results":
        tr = find_open_test_result_issues(context, consider_justification_rejection)
        return {"testResult": tr, "count": len(tr)}
    return {"count": 0}


def _find_next_imp_step(context: AssayContext) -> ImplementationStep | None:
    done = {c.step_id for c in context.impl_step_completions if c.done}
    ordered = sorted(context.ticket.implementation_steps, key=lambda s: s.order)
    return next((s for s in ordered if s.id not in done), None)


def _find_next_acceptance_criterion(context: AssayContext) -> AcceptanceCriterion | None:
    checked = {c.criterion_id for c in context.acceptance_checks if c.checked}
    ordered = sorted(context.ticket.acceptance_criteria, key=lambda a: a.order)
    return next((ac for ac in ordered if ac.id not in checked), None)


def _find_file_targets(context: AssayContext) -> list[dict[str, Any]]:
    declared = collect_declared_files(context.ticket)
    targets: list[dict[str, Any]] = []
    for d in declared:
        fc = next(
            (
                x
                for x in context.file_changes
                if x.expected_path == d.expected_path and x.expected_action == d.expected_action
            ),
            None,
        )
        if fc is None:
            targets.append({"expectedPath": d.expected_path, "expectedAction": d.expected_action})
            continue
        has_approved_just = bool(fc.justification) and fc.justification_approved == "approved"
        if fc.status != "matched" and not has_approved_just:
            targets.append({"expectedPath": d.expected_path, "expectedAction": d.expected_action})
    return targets


def _find_test_targets(context: AssayContext) -> list[dict[str, Any]]:
    spec = context.ticket.test_specification
    if spec is None:
        return []
    targets: list[dict[str, Any]] = []
    for test_type in spec.test_types:
        results = [r for r in context.test_results if r.test_type == test_type]
        has_passing = any(r.all_passed is True for r in results)
        has_justified_skip = any(
            r.skipped > 0 and len(r.skipped_justifications) > 0 for r in results
        )
        if not has_passing and not has_justified_skip:
            targets.append({"testType": test_type, "testCommands": list(spec.test_commands)})
    return targets


def _find_next_item_for(action: AssayAction, context: AssayContext) -> dict[str, Any]:
    if action == "check-imp-step":
        step = _find_next_imp_step(context)
        return {"hasNext": step is not None, "implStep": step}
    if action == "check-ac":
        ac = _find_next_acceptance_criterion(context)
        return {"hasNext": ac is not None, "acceptanceCriterion": ac}
    if action == "add-files-changes":
        targets = _find_file_targets(context)
        return {"hasNext": len(targets) > 0, "fileTargets": targets}
    targets = _find_test_targets(context)
    return {"hasNext": len(targets) > 0, "testTargets": targets}


def _aggregate_progress(context: AssayContext) -> CheckProgress:
    each = [
        compute_acceptance_progress(context),
        compute_impl_step_progress(context),
        compute_file_action_progress(context),
        compute_test_result_progress(context),
    ]
    return CheckProgress(
        total=sum(p.total for p in each),
        completed=sum(p.completed for p in each),
        remaining=0,
        remaining_ids=[],
    )


def _build_continue_step(
    action: AssayAction,
    items: dict[str, Any],
    context: AssayContext,
    reason: str,
) -> dict[str, Any] | None:
    progress = _progress_to_dict(_progress_for(action, context))

    if action == "check-imp-step":
        step: ImplementationStep | None = items.get("implStep")
        if step is None:
            return None
        return {
            "reason": reason,
            "action": "check-imp-step",
            "implStep": step.to_input_dict(),
            "progress": progress,
            "guidance": _placeholder_guidance(),
        }
    if action == "check-ac":
        ac: AcceptanceCriterion | None = items.get("acceptanceCriterion")
        if ac is None:
            return None
        return {
            "reason": reason,
            "action": "check-ac",
            "acceptanceCriterion": ac.to_input_dict(),
            "progress": progress,
            "guidance": _placeholder_guidance(),
        }
    if action == "add-files-changes":
        return {
            "reason": reason,
            "action": "add-files-changes",
            "targets": items.get("fileTargets") or [],
            "progress": progress,
            "guidance": _placeholder_guidance(),
        }
    return {
        "reason": reason,
        "action": "add-test-results",
        "targets": items.get("testTargets") or [],
        "progress": progress,
        "guidance": _placeholder_guidance(),
    }


def _build_resolve_step(
    action: AssayAction,
    issues: dict[str, Any],
    context: AssayContext,
    reason: str,
) -> dict[str, Any] | None:
    progress = _progress_to_dict(_progress_for(action, context))

    if action == "add-files-changes":
        if reason == "prerequisite":
            return {
                "reason": "prerequisite",
                "action": "add-files-changes",
                "targets": _find_file_targets(context),
                "progress": progress,
                "guidance": _placeholder_guidance(),
            }
        entries: list[FileChangeIssueEntry] = issues.get("fileChange") or []
        return {
            "reason": "resolve",
            "action": "add-files-changes",
            "issues": [
                {"fileChange": e.file_change.to_input_dict(), "issue": e.issue} for e in entries
            ],
            "progress": progress,
            "guidance": _placeholder_guidance(),
        }

    if action == "add-test-results":
        if reason == "prerequisite":
            return {
                "reason": "prerequisite",
                "action": "add-test-results",
                "targets": _find_test_targets(context),
                "progress": progress,
                "guidance": _placeholder_guidance(),
            }
        tentries: list[TestResultIssueEntry] = issues.get("testResult") or []
        return {
            "reason": "resolve",
            "action": "add-test-results",
            "issues": [
                {"testResult": e.test_result.to_input_dict(), "issue": e.issue} for e in tentries
            ],
            "progress": progress,
            "guidance": _placeholder_guidance(),
        }

    # For binary actions there are no "issues".
    return None


def resolve_next_step(context: AssayContext, options: AssayOptions) -> dict[str, Any] | None:
    if options.mode != "action":
        return None

    consider = options.consider_justification_rejection

    applicable = applicable_actions(context.ticket)
    if len(applicable) == 0:
        return {
            "reason": "complete",
            "progress": _progress_to_dict(_aggregate_progress(context)),
            "guidance": _placeholder_guidance(),
        }

    requested_action = options.action
    requested_idx = applicable.index(requested_action) if requested_action in applicable else -1
    effective_start = 0 if requested_idx == -1 else requested_idx

    # Priority 0 — Prerequisite (look back)
    for i in range(effective_start):
        earlier = applicable[i]
        issues = _find_issues_for(earlier, context, consider)
        if issues["count"] > 0:
            step = _build_resolve_step(earlier, issues, context, "prerequisite")
            if step is not None:
                return step
        items = _find_next_item_for(earlier, context)
        if items["hasNext"]:
            step = _build_continue_step(earlier, items, context, "prerequisite")
            if step is not None:
                return step

    # Priorities 1-2 — current and forward
    for i in range(effective_start, len(applicable)):
        current = applicable[i]
        issues = _find_issues_for(current, context, consider)
        if issues["count"] > 0:
            step = _build_resolve_step(current, issues, context, "resolve")
            if step is not None:
                return step
        items = _find_next_item_for(current, context)
        if items["hasNext"]:
            reason = "continue" if i == effective_start else "next-action"
            step = _build_continue_step(current, items, context, reason)
            if step is not None:
                return step

    # Priority 3 — Complete
    return {
        "reason": "complete",
        "progress": _progress_to_dict(_aggregate_progress(context)),
        "guidance": _placeholder_guidance(),
    }
