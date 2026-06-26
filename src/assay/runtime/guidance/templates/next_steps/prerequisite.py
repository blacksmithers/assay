"""Prerequisite (look-back) templates (port of ``templates/next-steps/prerequisite.ts``)."""

from __future__ import annotations

from typing import Any

from .template_types import NextStepTemplateOutput

_PREREQ_IMP_STEP = """Earlier action 'check-imp-step' has pending work.
 - Requested action: {requestedAction}
 - Next pending step: #{order} — {text}
 - Implementation progress: {progressCompleted}/{progressTotal} done

 The canonical sequence puts implementation steps before {requestedAction},
 because completed implementation usually resolves later actions naturally
 (e.g., file changes fall out of implementation work).

 Recommended moves:
 1. Execute the pending step as described
 2. Run mark_implementation_step_completion with done=true
 3. You may proceed with {requestedAction} if you have a strong reason to override the sequence — but the work session will not pass until prerequisites are addressed"""

_PREREQ_TESTS = """Earlier action 'add-test-results' has pending work.
 - Requested action: {requestedAction}
 - Pending test types: {pendingTypesList}
 - Test progress: {progressCompleted}/{progressTotal} satisfied

 Test results are typically registered before final actions because failing
 tests can change downstream conclusions (e.g., whether ACs are actually met).

 Recommended moves:
 1. Run the pending test types and register the outcomes via record_test_result
 2. Attach justifications via add_skip_justification or add_failure_justification as needed
 3. You may proceed with {requestedAction} if you have a strong reason to override — but the session will not pass until tests are recorded"""

_PREREQ_FILES = """Earlier action 'add-files-changes' has pending work.
 - Requested action: {requestedAction}
 - Pending file paths: {pendingPathsCount}
 - File-action progress: {progressCompleted}/{progressTotal} registered

 File actions are typically registered before AC verification because the
 ACs often reference behavior that depends on those files existing in the
 expected state.

 Recommended moves:
 1. Register the pending file actions via record_file_change
 2. Attach justifications via add_file_change_justification for any divergences
 3. You may proceed with {requestedAction} if you have a strong reason to override — but the session will not pass until files are registered"""

_PREREQ_AC = """Earlier action 'check-ac' has pending work.
 - Requested action: {requestedAction}
 - Next pending AC: #{order} — GIVEN {given} WHEN {when} THEN {then}
 - AC progress: {progressCompleted}/{progressTotal} verified

 Recommended moves:
 1. Verify the AC and run mark_acceptance_check with checked=true
 2. You may proceed with {requestedAction} if you have a strong reason to override"""


def prerequisite_imp_step_dispatcher(step: dict[str, Any]) -> NextStepTemplateOutput:
    if step["reason"] != "prerequisite" or step["action"] != "check-imp-step":
        raise ValueError("prerequisiteImpStepDispatcher: invalid step")
    return {
        "template": _PREREQ_IMP_STEP,
        "context": {
            "requestedAction": "<requestedAction>",
            "order": step["implStep"]["order"],
            "text": step["implStep"]["text"],
            "progressCompleted": step["progress"]["completed"],
            "progressTotal": step["progress"]["total"],
        },
        "operations": ["mark_implementation_step_completion"],
    }


def prerequisite_ac_dispatcher(step: dict[str, Any]) -> NextStepTemplateOutput:
    if step["reason"] != "prerequisite" or step["action"] != "check-ac":
        raise ValueError("prerequisiteAcDispatcher: invalid step")
    return {
        "template": _PREREQ_AC,
        "context": {
            "requestedAction": "<requestedAction>",
            "order": step["acceptanceCriterion"]["order"],
            "given": step["acceptanceCriterion"]["given"],
            "when": step["acceptanceCriterion"]["when"],
            "then": step["acceptanceCriterion"]["then"],
            "progressCompleted": step["progress"]["completed"],
            "progressTotal": step["progress"]["total"],
        },
        "operations": ["mark_acceptance_check"],
    }


def prerequisite_files_dispatcher(step: dict[str, Any]) -> NextStepTemplateOutput:
    if step["reason"] != "prerequisite" or step["action"] != "add-files-changes":
        raise ValueError("prerequisiteFilesDispatcher: invalid step")
    return {
        "template": _PREREQ_FILES,
        "context": {
            "requestedAction": "<requestedAction>",
            "pendingPathsCount": len(step["targets"]),
            "progressCompleted": step["progress"]["completed"],
            "progressTotal": step["progress"]["total"],
        },
        "operations": ["record_file_change", "add_file_change_justification"],
    }


def prerequisite_tests_dispatcher(step: dict[str, Any]) -> NextStepTemplateOutput:
    if step["reason"] != "prerequisite" or step["action"] != "add-test-results":
        raise ValueError("prerequisiteTestsDispatcher: invalid step")
    pending_types_list = (
        "(none)"
        if len(step["targets"]) == 0
        else ", ".join(t["testType"] for t in step["targets"])
    )
    return {
        "template": _PREREQ_TESTS,
        "context": {
            "requestedAction": "<requestedAction>",
            "pendingTypesList": pending_types_list,
            "progressCompleted": step["progress"]["completed"],
            "progressTotal": step["progress"]["total"],
        },
        "operations": ["record_test_result", "add_skip_justification"],
    }
