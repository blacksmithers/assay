"""Smoke tests for the public API surface."""

from __future__ import annotations

import re

import pytest

from assay import (
    ENGINE_VERSION,
    AssayContext,
    AssayOptions,
    assay,
    deterministic_id_generator,
    uuid_id_generator,
)

_TICKET = {
    "id": "T-1",
    "epicId": "E-1",
    "title": "Stub",
    "ticketType": "implementation",
    "complexity": "small",
    "estimatedMinutes": 30,
    "acceptanceCriteria": [{"id": "AC-1", "given": "g", "when": "w", "then": "t", "order": 1}],
    "implementationSteps": [{"id": "IS-1", "text": "do", "order": 1}],
    "filesToBeCreated": ["a.ts"],
    "filesToBeModified": [],
    "filesToBeDeleted": [],
    "filesToBeReferenced": [],
    "guardrails": [],
    "codeReferences": [],
    "typeReferences": [],
    "blueprintReferences": [],
    "dependencies": [],
}

_CONTEXT = {
    "ticket": _TICKET,
    "workSession": {
        "id": "ws-1",
        "ticketId": "T-1",
        "projectId": "p-1",
        "status": "active",
        "startedAt": "2026-01-01T00:00:00.000Z",
    },
    "acceptanceChecks": [
        {
            "id": "chk-AC-1",
            "workSessionId": "ws-1",
            "criterionId": "AC-1",
            "ticketId": "T-1",
            "projectId": "p-1",
            "checked": True,
        }
    ],
    "implStepCompletions": [
        {
            "id": "cpl-IS-1",
            "workSessionId": "ws-1",
            "stepId": "IS-1",
            "ticketId": "T-1",
            "projectId": "p-1",
            "done": True,
        }
    ],
    "fileChanges": [
        {
            "id": "fc-1",
            "workSessionId": "ws-1",
            "ticketId": "T-1",
            "projectId": "p-1",
            "expectedPath": "a.ts",
            "expectedAction": "create",
            "status": "matched",
            "justificationApproved": "pending",
            "recordedAt": "2026-01-01T00:00:00.000Z",
        }
    ],
    "testResults": [],
}


def test_engine_version() -> None:
    assert ENGINE_VERSION == "0.1.0"


def test_action_mode_complete() -> None:
    ctx = AssayContext.model_validate(_CONTEXT)
    result = assay(ctx, AssayOptions(mode="action", action="check-imp-step"))
    assert result.passed is True
    assert result.mode == "action"
    assert result.next_step is not None
    assert result.next_step["reason"] == "complete"
    assert result.summary is None


def test_check_mode_summary() -> None:
    ctx = AssayContext.model_validate(_CONTEXT)
    result = assay(ctx, AssayOptions(mode="check"))
    assert result.next_step is None
    assert result.summary is not None
    assert result.summary.total_pending == 0


def test_action_mode_requires_action() -> None:
    ctx = AssayContext.model_validate(_CONTEXT)
    with pytest.raises(ValueError):
        assay(ctx, AssayOptions(mode="action"))


def test_to_json_dict_shape() -> None:
    ctx = AssayContext.model_validate(_CONTEXT)
    result = assay(ctx, AssayOptions(mode="action", action="check-imp-step"))
    data = result.to_json_dict()
    assert set(data) == {"passed", "mode", "checks", "findings", "nextStep", "meta"}
    assert "generatedAt" in data["meta"]
    assert data["meta"]["engineVersion"] == "0.1.0"
    # 'summary' is unset in action mode → omitted (JSON.stringify semantics).
    assert "summary" not in data


def test_deterministic_id_is_stable() -> None:
    ctx = AssayContext.model_validate({**_CONTEXT, "implStepCompletions": []})
    opts = AssayOptions(
        mode="action", action="check-imp-step", id_generator=deterministic_id_generator
    )
    first = assay(ctx, opts).findings[0].id
    second = assay(ctx, opts).findings[0].id
    assert first == second
    assert re.fullmatch(r"[0-9a-f]{16}", first)


def test_uuid_id_generator_format() -> None:
    value = uuid_id_generator({"checkType": "x", "severity": "error", "entityIds": []})
    assert re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", value)
