"""Regression tests for JS-vs-Python parity edges found by the adversarial review.

These branches are not covered by the differential golden; each asserts the
behavior the reference TS engine produces (confirmed by running both engines
during the parity review).
"""

from __future__ import annotations

import pytest

from assay import (
    AssayContext,
    AssayOptions,
    ConfigValidationError,
    assay,
    deterministic_id_generator,
    load_defaults,
    merge_config,
    validate_config,
)
from assay.config import validate_safe_ranges
from assay.runtime.id_generator import _utf16_key


# 1. _deep_merge: a null/None override is a real value (JS skips only undefined).
def test_merge_none_primitive_override_raises() -> None:
    with pytest.raises(ConfigValidationError):
        merge_config(load_defaults(), {"checks": {"acceptance-coverage": {"enabled": None}}})


def test_merge_none_version_override_raises() -> None:
    with pytest.raises(ConfigValidationError):
        merge_config(load_defaults(), {"version": None})


def test_merge_none_object_override_raises() -> None:
    with pytest.raises(ConfigValidationError):
        merge_config(load_defaults(), {"checks": None})


# 2. version: z.literal(1) rejects booleans but accepts float 1.0.
def test_version_true_rejected() -> None:
    with pytest.raises(ConfigValidationError):
        validate_config({**load_defaults(), "version": True})


def test_version_float_one_accepted() -> None:
    assert validate_config({**load_defaults(), "version": 1.0})["version"] == 1


# 3. deterministic id sort: UTF-16 code unit (JS), not code point (Python).
def test_id_sort_matches_js_utf16_order() -> None:
    # 😀 (U+1F600, surrogate 0xD83D) sorts BEFORE Ａ (U+FF21) by UTF-16 code unit,
    # but AFTER it by code point. The id generator must use the JS ordering.
    assert _utf16_key("\U0001F600") < _utf16_key("Ａ")
    seed = {
        "checkType": "x",
        "severity": "error",
        "primaryEntityId": "p",
        "entityIds": ["\U0001F600", "Ａ"],
        "context": {},
    }
    # Stable + independent of input order (sorted internally to JS order).
    a = deterministic_id_generator(seed)
    b = deterministic_id_generator({**seed, "entityIds": ["Ａ", "\U0001F600"]})
    assert a == b


# 4. embedded testResult: explicit ``suites: null`` is kept; absent optional omitted.
def _failing_test_context(suites_present: bool) -> dict[str, object]:
    tr: dict[str, object] = {
        "id": "tr1",
        "workSessionId": "ws",
        "projectId": "p",
        "testType": "unit",
        "passed": 0,
        "failed": 1,
        "skipped": 0,
        "total": 1,
        "allPassed": False,
        "skippedJustifications": [],
        "failureJustifications": [],
        "runAt": "2026-01-01T00:00:00.000Z",
    }
    if suites_present:
        tr["suites"] = None
    return {
        "ticket": {
            "id": "T",
            "epicId": "E",
            "title": "t",
            "ticketType": "verification",
            "complexity": "small",
            "estimatedMinutes": 1,
            "acceptanceCriteria": [],
            "implementationSteps": [],
            "filesToBeCreated": [],
            "filesToBeModified": [],
            "filesToBeDeleted": [],
            "filesToBeReferenced": [],
            "guardrails": [],
            "codeReferences": [],
            "typeReferences": [],
            "blueprintReferences": [],
            "dependencies": [],
            "testSpecification": {
                "testTypes": ["unit"],
                "qualityGates": ["g"],
                "testCommands": ["npm test"],
            },
        },
        "workSession": {
            "id": "ws",
            "ticketId": "T",
            "projectId": "p",
            "status": "active",
            "startedAt": "2026-01-01T00:00:00.000Z",
        },
        "acceptanceChecks": [],
        "implStepCompletions": [],
        "fileChanges": [],
        "testResults": [tr],
    }


def test_embedded_explicit_null_suites_is_kept() -> None:
    ctx = AssayContext.model_validate(_failing_test_context(suites_present=True))
    result = assay(
        ctx,
        AssayOptions(
            mode="action", action="add-test-results", id_generator=deterministic_id_generator
        ),
    )
    assert result.next_step is not None
    assert result.next_step["reason"] == "resolve"
    embedded = result.next_step["issues"][0]["testResult"]
    assert "suites" in embedded
    assert embedded["suites"] is None


def test_embedded_absent_optional_is_omitted() -> None:
    ctx = AssayContext.model_validate(_failing_test_context(suites_present=False))
    result = assay(
        ctx,
        AssayOptions(
            mode="action", action="add-test-results", id_generator=deterministic_id_generator
        ),
    )
    assert result.next_step is not None
    embedded = result.next_step["issues"][0]["testResult"]
    assert "suites" not in embedded
    # absent optionals (command/output/...) are also omitted
    assert "command" not in embedded


# 5. validate_safe_ranges messages mirror JS typeof / String().
def test_safe_ranges_message_uses_js_typeof() -> None:
    cfg = validate_config(load_defaults())
    cfg["checks"]["acceptance-coverage"]["enabled"] = 1
    with pytest.raises(ConfigValidationError, match="must be boolean, got number"):
        validate_safe_ranges(cfg)


def test_safe_ranges_message_renders_undefined() -> None:
    cfg = validate_config(load_defaults())
    del cfg["checks"]["acceptance-coverage"]["severity"]
    with pytest.raises(ConfigValidationError, match="got undefined"):
        validate_safe_ranges(cfg)
