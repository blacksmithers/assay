"""File-action-coverage finding templates (port of ``findings/file-action-coverage.ts``)."""

from __future__ import annotations

from typing import Any

from .template_types import FindingTemplate

# C3.1 — missing, no justification, IS complete
_C3_1_COMPACT = """Planned file not registered (impl complete).
 - {expectedAction}: {expectedPath}

 Register via record_file_change or attach add_file_change_justification."""

_C3_1_VERBOSE = """A planned file action is missing.
 - Path: {expectedPath}
 - Expected action: {expectedAction}
 - Implementation steps: complete

 Implementation is fully recorded as done, so this gap is unlikely to resolve
 automatically. Either you have not registered the file change yet, or the
 file action was not executed.

 Possible reasons:
 - You executed the action but did not register it via record_file_change
 - The file was intentionally not touched (consider attaching a justification)
 - The spec is wrong about this file (consider reopening planning to remove it)

 Recommended moves:
 1. Run `git status` and `git diff` to confirm the local state of {expectedPath}
 2. If the file matches the expected action, register it via record_file_change with the matching actualAction (and optional commitHash for lifecycle validation)
 3. If the file was deliberately skipped, attach a reason via add_file_change_justification
 4. If the spec is wrong, reopen the planning session and adjust the filesToBe* lists"""

# C3.2 — missing, no justification, IS pending
_C3_2_COMPACT = """Planned file not yet registered.
 - {expectedAction}: {expectedPath}
 - Implementation still pending — likely auto-resolves

 No immediate action required."""

_C3_2_VERBOSE = """A planned file action is not yet registered.
 - Path: {expectedPath}
 - Expected action: {expectedAction}
 - Implementation steps: still pending

 Implementation is incomplete, so this gap will most likely resolve as you
 proceed with the implementation steps. No immediate action is required.

 Recommended moves:
 1. Continue with the next pending implementation step (see check-imp-step)
 2. Revisit this finding once implementation is complete — if the gap remains, register or justify"""

# C3.3 — mismatched, no justification
_C3_3_COMPACT = """File action diverges from plan.
 - {expectedPath}: planned {expectedAction}, recorded {actualAction}

 Correct via record_file_change or justify the divergence."""

_C3_3_VERBOSE = """A file was touched but with a different action than planned.
 - Path: {expectedPath}
 - Expected action: {expectedAction}
 - Recorded action: {actualAction}

 The spec planned one action, the agent recorded another. Either the spec was
 wrong, the agent diverged on purpose, or the recording is mistaken.

 Possible reasons:
 - The actual action you took was correct; the spec was outdated
 - You took a different action than planned and need to justify the divergence
 - The recording was a mistake (you took the planned action but recorded the wrong one)

 Recommended moves:
 1. Confirm via `git status`/`git diff` what action was actually performed
 2. If the recording is wrong, run record_file_change with the correct actualAction
 3. If the divergence is intentional, attach add_file_change_justification explaining why
 4. If the spec is wrong, reopen the planning session to update the filesToBe* lists"""

# C3.4 — extra, no justification
_C3_4_COMPACT = """File touched but not in spec.
 - {expectedPath} ({actualAction})

 Add to filesToBe* via planning OR justify via add_file_change_justification."""

_C3_4_VERBOSE = """A file was touched without being declared in the spec.
 - Path: {expectedPath}
 - Recorded action: {actualAction}

 The spec does not list this file in any filesToBe* group, but the agent
 registered a change for it. Untracked file changes erode planning fidelity
 and should be either declared or justified.

 Possible reasons:
 - The file is genuinely necessary for the work but was missed during planning
 - The file is incidental (e.g., generated artifact, lockfile update) and warrants justification
 - The recording was mistaken (the file should not appear at all)

 Recommended moves:
 1. Decide whether the change is essential to the ticket or peripheral
 2. If essential, reopen the planning session to add the file to the appropriate filesToBe* list
 3. If peripheral but legitimate, attach add_file_change_justification explaining why
 4. If the recording was wrong, the operations layer rejects deletes — contact lifecycle to clean up"""

# C3.5 — pending justification (warn)
_C3_5_COMPACT = """Justification awaiting approval.
 - {expectedPath} ({status})

 No action required."""

_C3_5_VERBOSE = """A justification was provided and is awaiting approval.
 - Path: {expectedPath}
 - Status: {status} ({expectedAction} -> {actualAction})
 - Approval state: pending

 The justification you submitted has not yet been accepted or rejected.
 The work session will be re-evaluated automatically when the approval state changes.

 Recommended moves:
 1. No further action is required from you for this entry
 2. Continue with other pending items in this work session"""

# C3.6 — rejected justification (gated)
_C3_6_COMPACT = """Justification rejected — review file action.
 - {expectedPath} ({status})

 Correct via record_file_change OR amend_file_change_justification."""

_C3_6_VERBOSE = """Justification not accepted — review file action.
 - Path: {expectedPath}
 - Status: {status} ({expectedAction} -> {actualAction})
 - Approval state: rejected

 The reviewer rejected the justification you provided. The divergence remains
 unresolved. Either the action was wrong, the justification was not strong enough,
 or the spec needs updating.

 Possible reasons:
 - The reviewer believed the planned action was still correct and should be performed
 - The justification did not adequately explain the divergence
 - The reviewer wants the spec amended instead of justified

 Recommended moves:
 1. Re-read the rejection context (typically passed alongside this finding)
 2. If the planned action should have been taken, run record_file_change with the corrected outcome
 3. If the justification needs rework, run amend_file_change_justification with stronger reasoning
 4. If the spec is wrong, reopen the planning session"""

# C3.7 — data-integrity (system error)
_C3_7_COMPACT = """Data integrity error: untagged extra file.
 - {expectedPath} ({actualAction})

 System bug — agent cannot resolve. Surface to operations maintainer."""

_C3_7_VERBOSE = """Data integrity error: file change recorded but not declared, and not tagged 'extra'.
 - Path: {expectedPath}
 - Recorded action: {actualAction}

 The ingestion layer should tag any FileChange with no matching declared entry
 as status='extra'. This entry has neither a declared match nor the 'extra' tag,
 indicating a bug in the ingestion / operations layer.

 This is NOT something the agent can fix. The work session is currently blocked
 by a system inconsistency.

 Recommended moves:
 1. Surface this finding to the operations / lifecycle maintainer
 2. Continue with other pending items in this work session if any are unblocked"""

_T_3_1: FindingTemplate = {
    "compact": _C3_1_COMPACT,
    "verbose": _C3_1_VERBOSE,
    "operations": ["record_file_change", "add_file_change_justification"],
}
_T_3_2: FindingTemplate = {
    "compact": _C3_2_COMPACT,
    "verbose": _C3_2_VERBOSE,
    "operations": [],
}
_T_3_3: FindingTemplate = {
    "compact": _C3_3_COMPACT,
    "verbose": _C3_3_VERBOSE,
    "operations": ["record_file_change", "add_file_change_justification"],
}
_T_3_4: FindingTemplate = {
    "compact": _C3_4_COMPACT,
    "verbose": _C3_4_VERBOSE,
    "operations": ["add_file_change_justification"],
}
_T_3_5: FindingTemplate = {
    "compact": _C3_5_COMPACT,
    "verbose": _C3_5_VERBOSE,
    "operations": [],
}
_T_3_6: FindingTemplate = {
    "compact": _C3_6_COMPACT,
    "verbose": _C3_6_VERBOSE,
    "operations": ["record_file_change", "amend_file_change_justification"],
}
_T_3_7: FindingTemplate = {
    "compact": _C3_7_COMPACT,
    "verbose": _C3_7_VERBOSE,
    "operations": [],
}


def file_action_coverage_dispatcher(ctx: dict[str, Any]) -> FindingTemplate:
    if ctx.get("issue") == "data-integrity":
        return _T_3_7

    status = ctx.get("status")
    has_justification = bool(ctx.get("hasJustification"))
    justification_approved = ctx.get("justificationApproved")
    is_impl_complete = ctx.get("isImplComplete") is not False

    if has_justification and justification_approved == "rejected":
        return _T_3_6
    if has_justification and justification_approved == "pending":
        return _T_3_5

    if status == "mismatched":
        return _T_3_3
    if status == "extra":
        return _T_3_4
    if status == "missing":
        return _T_3_1 if is_impl_complete else _T_3_2

    # Unrecognized — fall back to mismatched template.
    return _T_3_3
