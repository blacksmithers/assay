"""Check-mode summary templates (port of ``templates/summary.ts``)."""

from __future__ import annotations

from dataclasses import dataclass

from ...enums import AssayAction

SUMMARY_TEMPLATE = """Ticket completion status:

{pendingByActionList}

 Total pending: {totalPending} items, {blockingIssues} blocking issue(s).

 Start here:
{startPointBlock}

{trailingHint}"""

SP_A_TEMPLATE = """ 1. Resolve the open issue(s) first — they block any successful completion.
    First issue: {firstIssueLabel} on {firstIssuePath}
    Action involved: {firstIssueAction}

 2. After resolving issues, return here for the next pending action."""

SP_B_TEMPLATE = """ 1. {firstPendingAction}: {firstPendingItemSummary}
    Progress: {firstPendingActionCompleted}/{firstPendingActionTotal}

 2. Switch to mode='action' with action='{firstPendingAction}' for step-by-step guidance."""

SP_C_TEMPLATE = """ The work session is ready for closure. Invoke complete_work_session."""

TRAILING_HINT_ISSUES = """Each issue has its own compact guidance in the findings list above.
 Switch to mode='action' for verbose remediation guidance on a specific issue."""

TRAILING_HINT_PENDING = """Switch to mode='action' to receive verbose step-by-step guidance.
 Canonical sequence: check-imp-step → add-test-results → add-files-changes → check-ac."""

TRAILING_HINT_COMPLETE = """All applicable actions are complete and no blocking issues remain.
 Invoke complete_work_session to close the work session."""


@dataclass
class PendingByActionLine:
    action: AssayAction
    pending: int
    issues: int


def render_pending_by_action(
    lines: list[PendingByActionLine],
    applicable: list[AssayAction],
) -> str:
    ordered: list[AssayAction] = [
        "check-imp-step",
        "add-test-results",
        "add-files-changes",
        "check-ac",
    ]
    out: list[str] = []
    for action in ordered:
        if action not in applicable:
            continue
        line = next((line_ for line_ in lines if line_.action == action), None)
        if line is None or line.pending == 0:
            continue
        row = f" - {action}: {line.pending} pending"
        if line.issues > 0:
            row += f" ({line.issues} issue(s))"
        out.append(row)
    return "\n".join(out)
