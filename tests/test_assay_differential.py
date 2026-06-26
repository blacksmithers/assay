"""Differential: assay() output vs golden captured from the reference TS engine.

The golden files under ``fixtures/golden/`` are the committed TS test-surface
snapshots (normalized ``assay()`` output, deterministic ids, ``generatedAt``
excluded). This test replays the same seeds through the Python engine, applies
the identical normalization (port of ``scripts/run-test-surface.ts``
``normalizeResult`` / ``applyDelta``), and asserts structural equality.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from assay import assay, deterministic_id_generator
from assay.types import AssayContext, AssayOptions

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "fixtures" / "seeds"
GOLDEN = ROOT / "fixtures" / "golden"


# ---------------- normalization (port of run-test-surface.ts) ----------------


def _finding_sort_key(f: Any) -> tuple[str, str, str, str]:
    return (f.check_type, f.severity, f.primary_entity_id, f.id)


def _normalize_check(check: Any) -> dict[str, Any]:
    return {
        "checkType": check.check_type,
        "passed": check.passed,
        "progress": check.progress.to_json_dict(),
        "findings": [f.to_json_dict() for f in sorted(check.findings, key=_finding_sort_key)],
    }


def _normalize_result(result: Any) -> dict[str, Any]:
    sorted_findings = sorted(result.findings, key=_finding_sort_key)
    return {
        "passed": result.passed,
        "mode": result.mode,
        "checks": {
            "acceptanceCoverage": _normalize_check(result.checks.acceptance_coverage),
            "implementationCoverage": _normalize_check(result.checks.implementation_coverage),
            "fileActionCoverage": _normalize_check(result.checks.file_action_coverage),
            "testResultPresence": _normalize_check(result.checks.test_result_presence),
        },
        "findings": [f.to_json_dict() for f in sorted_findings],
        "nextStep": result.next_step if result.next_step is not None else None,
        "summary": result.summary.to_json_dict() if result.summary is not None else None,
        "meta": {
            "engineVersion": result.meta.engine_version,
            "configHash": result.meta.config_hash,
        },
    }


# ---------------- context delta (port of run-test-surface.ts) ----------------


def _apply_updates(rows: list[dict[str, Any]], updates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {u["id"]: u["patch"] for u in updates}
    return [{**row, **by_id[row["id"]]} if row["id"] in by_id else row for row in rows]


def _apply_delta(context: dict[str, Any], delta: dict[str, Any] | None) -> dict[str, Any]:
    if not delta:
        return context

    acceptance_checks = context["acceptanceChecks"]
    impl_step_completions = context["implStepCompletions"]
    file_changes = context["fileChanges"]
    test_results = context["testResults"]

    if delta.get("addAcceptanceChecks"):
        acceptance_checks = [*acceptance_checks, *delta["addAcceptanceChecks"]]
    if delta.get("addImplStepCompletions"):
        impl_step_completions = [*impl_step_completions, *delta["addImplStepCompletions"]]
    if delta.get("addFileChanges"):
        file_changes = [*file_changes, *delta["addFileChanges"]]
    if delta.get("addTestResults"):
        test_results = [*test_results, *delta["addTestResults"]]

    if delta.get("updateAcceptanceChecks"):
        acceptance_checks = _apply_updates(acceptance_checks, delta["updateAcceptanceChecks"])
    if delta.get("updateImplStepCompletions"):
        impl_step_completions = _apply_updates(
            impl_step_completions, delta["updateImplStepCompletions"]
        )
    if delta.get("updateFileChanges"):
        file_changes = _apply_updates(file_changes, delta["updateFileChanges"])
    if delta.get("updateTestResults"):
        test_results = _apply_updates(test_results, delta["updateTestResults"])

    ticket = context["ticket"]
    if delta.get("ticketPatch"):
        ticket = {**ticket, **delta["ticketPatch"]}

    return {
        **context,
        "ticket": ticket,
        "acceptanceChecks": acceptance_checks,
        "implStepCompletions": impl_step_completions,
        "fileChanges": file_changes,
        "testResults": test_results,
    }


def _run(context_dict: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    ctx = AssayContext.model_validate(context_dict)
    opts = AssayOptions(
        mode=options["mode"],
        action=options.get("action"),
        consider_justification_rejection=options.get("considerJustificationRejection", False),
        id_generator=deterministic_id_generator,
    )
    return _normalize_result(assay(ctx, opts))


# ---------------------------------- cases ------------------------------------

_SINGLE_CASES = sorted(p.stem for p in (SEEDS / "single").glob("*.json"))

_FLOW_CASES: list[tuple[str, int]] = []
for _flow_path in sorted((SEEDS / "flows").glob("*.json")):
    _flow = json.loads(_flow_path.read_text(encoding="utf-8"))
    for _i in range(len(_flow["steps"])):
        _FLOW_CASES.append((_flow["name"], _i + 1))


@pytest.mark.parametrize("name", _SINGLE_CASES)
def test_single_matches_golden(name: str) -> None:
    seed = json.loads((SEEDS / "single" / f"{name}.json").read_text(encoding="utf-8"))
    actual = _run(seed["context"], seed["options"])
    golden = json.loads((GOLDEN / "single" / f"{name}.json").read_text(encoding="utf-8"))
    assert actual == golden


@pytest.mark.parametrize("flow_name,step", _FLOW_CASES)
def test_flow_matches_golden(flow_name: str, step: int) -> None:
    seed = json.loads((SEEDS / "flows" / f"{flow_name}.json").read_text(encoding="utf-8"))
    context = seed["initialContext"]
    for i, step_def in enumerate(seed["steps"]):
        context = _apply_delta(context, step_def.get("contextDelta"))
        if i + 1 != step:
            continue
        actual = _normalize_result(
            _run_assay(context, step_def["options"])
        )
        golden = json.loads(
            (GOLDEN / "flows" / flow_name / f"step-{step:02d}.json").read_text(encoding="utf-8")
        )
        assert actual == golden
        return


def _run_assay(context_dict: dict[str, Any], options: dict[str, Any]) -> Any:
    ctx = AssayContext.model_validate(context_dict)
    opts = AssayOptions(
        mode=options["mode"],
        action=options.get("action"),
        consider_justification_rejection=options.get("considerJustificationRejection", False),
        id_generator=deterministic_id_generator,
    )
    return assay(ctx, opts)
