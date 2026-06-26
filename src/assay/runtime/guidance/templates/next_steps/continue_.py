"""Continue / next-action templates (port of ``templates/next-steps/continue.ts``)."""

from __future__ import annotations

from typing import Any

from .template_types import NextStepTemplateOutput

_CONTINUE_IMP_STEP = """Next implementation step to complete:
 - Position: {order} of {progressTotal}
 - Progress: {progressCompleted} done, {progressRemaining} remaining
 - Text: {text}

 Execute the step as described. Once the work for this step is complete,
 record completion so the engine advances to the next step or action.

 Recommended moves:
 1. Read the text carefully and execute the implied work
 2. Run mark_implementation_step_completion with done=true to advance"""

_CONTINUE_AC = """Next acceptance criterion to verify:
 - Position: {order} of {progressTotal}
 - Progress: {progressCompleted} verified, {progressRemaining} remaining
 - GIVEN: {given}
 - WHEN: {when}
 - THEN: {then}

 Verify that the implemented behavior matches every GIVEN/WHEN/THEN clause.
 Acceptance criteria are typically the last action in a work session — if
 you're here, implementation, tests, and file changes should already be done.

 Recommended moves:
 1. Examine the implementation against the BDD clauses above
 2. If the behavior matches, run mark_acceptance_check with checked=true
 3. If the behavior does not match, return to check-imp-step or add-files-changes to fix"""

_CONTINUE_FILES = """File actions pending registration ({progressRemaining} of {progressTotal}):

{targetsList}

 The spec lists these file paths and actions; you need to register what
 actually happened during implementation. Each entry needs an actualAction
 (created/modified/deleted/referenced/absent) and a status (matched if it went
 as planned, mismatched/missing/extra otherwise).

 Recommended moves:
 1. Run `git status` and `git log` to verify what changed
 2. For each entry above, run record_file_change with the actualAction, status, and optional commitHash
 3. If any registration diverges from the planned action, attach add_file_change_justification explaining why"""

_CONTINUE_TESTS = """Test types pending recording ({progressRemaining} of {progressTotal}):

{targetsList}

 The spec requires these test types. For each, run the corresponding command(s),
 register the outcome (pass/fail/skip counts), and attach justifications for any
 skipped or failing tests.

 Recommended moves:
 1. Run the test command(s) for each pending type
 2. For each run, register the outcome via record_test_result
 3. If any tests are skipped, attach justifications via add_skip_justification
 4. If any tests fail and the failures are acceptable, attach add_failure_justification"""


def _render_file_targets(targets: list[dict[str, Any]]) -> str:
    if len(targets) == 0:
        return " - (none)"
    return "\n".join(f" - {t['expectedAction']}: {t['expectedPath']}" for t in targets)


def _render_test_targets(targets: list[dict[str, Any]]) -> str:
    if len(targets) == 0:
        return " - (none)"
    return "\n".join(
        f" - {t['testType']} (commands: {', '.join(t['testCommands']) or 'n/a'})" for t in targets
    )


def continue_imp_step_dispatcher(step: dict[str, Any]) -> NextStepTemplateOutput:
    if step["reason"] == "complete" or step["action"] != "check-imp-step":
        raise ValueError("continueImpStepDispatcher: invalid step")
    return {
        "template": _CONTINUE_IMP_STEP,
        "context": {
            "order": step["implStep"]["order"],
            "text": step["implStep"]["text"],
            "progressTotal": step["progress"]["total"],
            "progressCompleted": step["progress"]["completed"],
            "progressRemaining": step["progress"]["remaining"],
        },
        "operations": ["mark_implementation_step_completion"],
    }


def continue_ac_dispatcher(step: dict[str, Any]) -> NextStepTemplateOutput:
    if step["reason"] == "complete" or step["action"] != "check-ac":
        raise ValueError("continueAcDispatcher: invalid step")
    return {
        "template": _CONTINUE_AC,
        "context": {
            "order": step["acceptanceCriterion"]["order"],
            "given": step["acceptanceCriterion"]["given"],
            "when": step["acceptanceCriterion"]["when"],
            "then": step["acceptanceCriterion"]["then"],
            "progressTotal": step["progress"]["total"],
            "progressCompleted": step["progress"]["completed"],
            "progressRemaining": step["progress"]["remaining"],
        },
        "operations": ["mark_acceptance_check"],
    }


def continue_files_dispatcher(step: dict[str, Any]) -> NextStepTemplateOutput:
    if (
        step["reason"] == "complete"
        or step["action"] != "add-files-changes"
        or step["reason"] == "resolve"
    ):
        raise ValueError("continueFilesDispatcher: invalid step")
    return {
        "template": _CONTINUE_FILES,
        "context": {
            "progressTotal": step["progress"]["total"],
            "progressCompleted": step["progress"]["completed"],
            "progressRemaining": step["progress"]["remaining"],
            "targetsList": _render_file_targets(step["targets"]),
        },
        "operations": ["record_file_change", "add_file_change_justification"],
    }


def continue_tests_dispatcher(step: dict[str, Any]) -> NextStepTemplateOutput:
    if (
        step["reason"] == "complete"
        or step["action"] != "add-test-results"
        or step["reason"] == "resolve"
    ):
        raise ValueError("continueTestsDispatcher: invalid step")
    return {
        "template": _CONTINUE_TESTS,
        "context": {
            "progressTotal": step["progress"]["total"],
            "progressCompleted": step["progress"]["completed"],
            "progressRemaining": step["progress"]["remaining"],
            "targetsList": _render_test_targets(step["targets"]),
        },
        "operations": [
            "record_test_result",
            "add_skip_justification",
            "add_failure_justification",
        ],
    }
