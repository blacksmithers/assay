"""Operations vocabulary (port of ``runtime/operations-registry.ts``)."""

from __future__ import annotations

from typing import Literal

from typing_extensions import TypedDict

OperationName = Literal[
    "mark_acceptance_check",
    "mark_implementation_step_completion",
    "record_file_change",
    "add_file_change_justification",
    "amend_file_change_justification",
    "record_test_result",
    "add_skip_justification",
    "amend_skip_justification",
    "add_failure_justification",
    "amend_failure_justification",
    "complete_work_session",
]


class OperationDef(TypedDict):
    name: OperationName
    description: str
    parameterShape: str
    applicability: Literal["finding-level", "session-level"]


OPERATIONS: dict[OperationName, OperationDef] = {
    "mark_acceptance_check": {
        "name": "mark_acceptance_check",
        "description": (
            "Record that an acceptance criterion has been verified for the current work session."
        ),
        "parameterShape": "{ workSessionId, criterionId, checked: boolean }",
        "applicability": "finding-level",
    },
    "mark_implementation_step_completion": {
        "name": "mark_implementation_step_completion",
        "description": (
            "Record that an implementation step has been completed for the current work session."
        ),
        "parameterShape": "{ workSessionId, stepId, done: boolean }",
        "applicability": "finding-level",
    },
    "record_file_change": {
        "name": "record_file_change",
        "description": (
            "Record the actual outcome of a planned file action (create/modify/delete/reference). "
            "Includes optional commitHash for lifecycle git-validation."
        ),
        "parameterShape": (
            "{ workSessionId, ticketId, expectedPath, expectedAction, actualAction, status, "
            "notes?, lineCount?, commitHash? }"
        ),
        "applicability": "finding-level",
    },
    "add_file_change_justification": {
        "name": "add_file_change_justification",
        "description": (
            "Attach a justification when an executed file action diverges from the planned one."
        ),
        "parameterShape": "{ fileChangeId, justification: string }",
        "applicability": "finding-level",
    },
    "amend_file_change_justification": {
        "name": "amend_file_change_justification",
        "description": (
            "Replace an existing justification — typically used after a justification was rejected."
        ),
        "parameterShape": "{ fileChangeId, justification: string }",
        "applicability": "finding-level",
    },
    "record_test_result": {
        "name": "record_test_result",
        "description": (
            "Record the outcome of a test execution (pass/fail/skip counts, output, command, etc.)."
        ),
        "parameterShape": (
            "{ workSessionId, testType, command, passed, failed, skipped, total, allPassed, ... }"
        ),
        "applicability": "finding-level",
    },
    "add_skip_justification": {
        "name": "add_skip_justification",
        "description": (
            "Add justification entries for tests that were skipped during a recorded test run."
        ),
        "parameterShape": "{ testResultId, justifications: string[] }",
        "applicability": "finding-level",
    },
    "amend_skip_justification": {
        "name": "amend_skip_justification",
        "description": "Replace skip justifications — typically used after rejection.",
        "parameterShape": "{ testResultId, justifications: string[] }",
        "applicability": "finding-level",
    },
    "add_failure_justification": {
        "name": "add_failure_justification",
        "description": (
            "Add justification entries for tests that failed but are accepted as known/intentional."
        ),
        "parameterShape": "{ testResultId, justifications: string[] }",
        "applicability": "finding-level",
    },
    "amend_failure_justification": {
        "name": "amend_failure_justification",
        "description": "Replace failure justifications — typically used after rejection.",
        "parameterShape": "{ testResultId, justifications: string[] }",
        "applicability": "finding-level",
    },
    "complete_work_session": {
        "name": "complete_work_session",
        "description": (
            "Close the work session as fully completed — every applicable action exhausted, "
            "no blocking issues."
        ),
        "parameterShape": "{ workSessionId }",
        "applicability": "session-level",
    },
}

OPERATION_NAMES: tuple[OperationName, ...] = tuple(OPERATIONS.keys())


def is_operation_name(value: str) -> bool:
    return value in OPERATIONS
