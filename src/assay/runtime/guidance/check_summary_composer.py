"""Check-mode summary composer (port of ``guidance/check-summary-composer.ts``)."""

from __future__ import annotations

from dataclasses import dataclass

from ..enums import ASSAY_ACTIONS, AssayAction
from ..issues.file_change_issues import FileChangeIssueEntry, find_open_file_change_issues
from ..issues.test_result_issues import TestResultIssueEntry, find_open_test_result_issues
from ..next_step.applicability import applicable_actions
from ..progress.acceptance import compute_acceptance_progress
from ..progress.file_action import compute_file_action_progress
from ..progress.impl_step import compute_impl_step_progress
from ..progress.test_result import compute_test_result_progress
from ..types.context import AssayContext
from ..types.finding import Finding
from ..types.result import CheckModeSummary
from .interpolate import interpolate
from .templates.next_steps.resolve import FILE_ISSUE_LABEL, TEST_ISSUE_LABEL
from .templates.summary import (
    SP_A_TEMPLATE,
    SP_B_TEMPLATE,
    SP_C_TEMPLATE,
    SUMMARY_TEMPLATE,
    TRAILING_HINT_COMPLETE,
    TRAILING_HINT_ISSUES,
    TRAILING_HINT_PENDING,
    PendingByActionLine,
    render_pending_by_action,
)


@dataclass
class CheckSummaryComposeInput:
    context: AssayContext
    findings: list[Finding]
    consider_justification_rejection: bool


def compose_check_summary(inp: CheckSummaryComposeInput) -> CheckModeSummary:
    context = inp.context
    findings = inp.findings
    consider_justification_rejection = inp.consider_justification_rejection

    applicable = applicable_actions(context.ticket)

    pending_by_action: dict[str, int] = {
        "check-imp-step": compute_impl_step_progress(context).remaining,
        "add-test-results": compute_test_result_progress(context).remaining,
        "add-files-changes": compute_file_action_progress(context).remaining,
        "check-ac": compute_acceptance_progress(context).remaining,
    }
    for a in ASSAY_ACTIONS:
        if a not in applicable:
            pending_by_action[a] = 0

    file_issues = find_open_file_change_issues(context, consider_justification_rejection)
    test_issues = find_open_test_result_issues(context, consider_justification_rejection)

    issues_by_action: dict[str, int] = {
        "check-imp-step": 0,
        "add-test-results": len(test_issues),
        "add-files-changes": len(file_issues),
        "check-ac": 0,
    }

    total_pending = sum(pending_by_action.values())
    blocking_issues = sum(1 for f in findings if f.severity == "error")

    lines = [
        PendingByActionLine(
            action=action,
            pending=pending_by_action[action],
            issues=issues_by_action[action],
        )
        for action in ASSAY_ACTIONS
    ]

    pending_by_action_list = render_pending_by_action(lines, applicable)

    start_point_block = _compose_start_point(
        file_issues, test_issues, pending_by_action, applicable, context
    )

    trailing_hint = _compose_trailing_hint(blocking_issues, total_pending)

    message = interpolate(
        SUMMARY_TEMPLATE,
        {
            "pendingByActionList": pending_by_action_list or " - (no actions applicable)",
            "totalPending": total_pending,
            "blockingIssues": blocking_issues,
            "startPointBlock": start_point_block,
            "trailingHint": trailing_hint,
        },
    )

    return CheckModeSummary(
        message=message,
        pending_by_action=pending_by_action,
        total_pending=total_pending,
        blocking_issues=blocking_issues,
    )


def _compose_start_point(
    file_issues: list[FileChangeIssueEntry],
    test_issues: list[TestResultIssueEntry],
    pending_by_action: dict[str, int],
    applicable: list[AssayAction],
    context: AssayContext,
) -> str:
    has_issues = len(file_issues) > 0 or len(test_issues) > 0
    if has_issues:
        first_file_time = file_issues[0].file_change.recorded_at if file_issues else "￿"
        first_test_time = test_issues[0].test_result.run_at if test_issues else "￿"
        if first_file_time <= first_test_time and file_issues:
            first_f = file_issues[0]
            return interpolate(
                SP_A_TEMPLATE,
                {
                    "firstIssueLabel": FILE_ISSUE_LABEL[first_f.issue],
                    "firstIssuePath": first_f.file_change.expected_path,
                    "firstIssueAction": "add-files-changes",
                },
            )
        if test_issues:
            first_t = test_issues[0]
            return interpolate(
                SP_A_TEMPLATE,
                {
                    "firstIssueLabel": TEST_ISSUE_LABEL[first_t.issue],
                    "firstIssuePath": first_t.test_result.test_type,
                    "firstIssueAction": "add-test-results",
                },
            )

    sequence: list[AssayAction] = [
        "check-imp-step",
        "add-test-results",
        "add-files-changes",
        "check-ac",
    ]
    first_pending = next(
        (a for a in sequence if a in applicable and pending_by_action[a] > 0), None
    )
    if first_pending is not None:
        summary = _first_pending_item_summary(first_pending, context)
        completed = _completed_for(first_pending, context)
        total = _total_for(first_pending, context)
        return interpolate(
            SP_B_TEMPLATE,
            {
                "firstPendingAction": first_pending,
                "firstPendingItemSummary": summary,
                "firstPendingActionCompleted": completed,
                "firstPendingActionTotal": total,
            },
        )

    return SP_C_TEMPLATE


def _first_pending_item_summary(action: AssayAction, context: AssayContext) -> str:
    if action == "check-imp-step":
        progress = compute_impl_step_progress(context)
        return (
            f"next step {progress.next_in_order_id}"
            if progress.next_in_order_id
            else f"{progress.remaining} pending"
        )
    if action == "check-ac":
        progress = compute_acceptance_progress(context)
        return (
            f"next AC {progress.next_in_order_id}"
            if progress.next_in_order_id
            else f"{progress.remaining} pending"
        )
    if action == "add-files-changes":
        progress = compute_file_action_progress(context)
        return f"{progress.remaining} file action(s) pending"
    progress = compute_test_result_progress(context)
    return f"{progress.remaining} test type(s) pending"


def _completed_for(action: AssayAction, context: AssayContext) -> int:
    if action == "check-imp-step":
        return compute_impl_step_progress(context).completed
    if action == "check-ac":
        return compute_acceptance_progress(context).completed
    if action == "add-files-changes":
        return compute_file_action_progress(context).completed
    return compute_test_result_progress(context).completed


def _total_for(action: AssayAction, context: AssayContext) -> int:
    if action == "check-imp-step":
        return compute_impl_step_progress(context).total
    if action == "check-ac":
        return compute_acceptance_progress(context).total
    if action == "add-files-changes":
        return compute_file_action_progress(context).total
    return compute_test_result_progress(context).total


def _compose_trailing_hint(blocking_issues: int, total_pending: int) -> str:
    if blocking_issues > 0:
        return TRAILING_HINT_ISSUES
    if total_pending > 0:
        return TRAILING_HINT_PENDING
    return TRAILING_HINT_COMPLETE
