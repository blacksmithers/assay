"""Engine entry point (port of ``runtime/assay.ts``)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ..config.hash import config_hash
from ..config.loader import load_defaults
from .checks import CHECK_REGISTRY, CheckOutput, CheckRunOptions
from .guidance.check_summary_composer import CheckSummaryComposeInput, compose_check_summary
from .guidance.finding_composer import GuidanceVerbosity, compose_finding_guidance
from .guidance.next_step_composer import NextStepComposeOptions, compose_next_step_guidance
from .id_generator import IdGenerator, uuid_id_generator
from .next_step.resolver import resolve_next_step
from .progress.neutral import neutral_progress
from .types.check_result import CheckResult
from .types.context import AssayContext
from .types.finding import AssayCheckType, Finding
from .types.options import AssayOptions
from .types.progress import CheckProgress
from .types.result import AssayChecks, AssayMode, AssayResult, AssayResultMeta
from .version import ENGINE_VERSION


def assay(context: AssayContext, options: AssayOptions) -> AssayResult:
    if options.mode == "action" and not options.action:
        raise ValueError(
            "assay(): options.action is required when options.mode === 'action'"
        )

    generate_id = options.id_generator or uuid_id_generator
    consider_justification_rejection = options.consider_justification_rejection
    config = context.config if context.config is not None else load_defaults()
    run_options = CheckRunOptions(
        config=config,
        consider_justification_rejection=consider_justification_rejection,
    )

    acceptance = _run_check("acceptance-coverage", context, generate_id, run_options)
    implementation = _run_check("implementation-coverage", context, generate_id, run_options)
    file_action = _run_check("file-action-coverage", context, generate_id, run_options)
    test_result = _run_check("test-result-presence", context, generate_id, run_options)

    next_step = resolve_next_step(context, options) if options.mode == "action" else None

    raw_findings: list[Finding] = [
        *acceptance.findings,
        *implementation.findings,
        *file_action.findings,
        *test_result.findings,
    ]

    anchor_entity_id = _resolve_anchor_entity_id(next_step) if next_step is not None else None

    all_findings: list[Finding] = []
    for finding in raw_findings:
        verbosity = _dispatch_verbosity(finding, options.mode, anchor_entity_id)
        guidance = compose_finding_guidance(finding, verbosity)
        all_findings.append(finding.model_copy(update={"guidance": guidance}))

    findings_by_check = _group_by_check(all_findings)
    checks = AssayChecks(
        acceptance_coverage=_to_check_result(
            "acceptance-coverage", findings_by_check["acceptance-coverage"], acceptance.progress
        ),
        implementation_coverage=_to_check_result(
            "implementation-coverage",
            findings_by_check["implementation-coverage"],
            implementation.progress,
        ),
        file_action_coverage=_to_check_result(
            "file-action-coverage", findings_by_check["file-action-coverage"], file_action.progress
        ),
        test_result_presence=_to_check_result(
            "test-result-presence", findings_by_check["test-result-presence"], test_result.progress
        ),
    )

    passed = not any(f.severity == "error" for f in all_findings)

    kwargs: dict[str, Any] = {
        "passed": passed,
        "mode": options.mode,
        "checks": checks,
        "findings": all_findings,
        "meta": AssayResultMeta(
            engine_version=ENGINE_VERSION,
            generated_at=_now_iso(),
            config_hash=config_hash(config),
        ),
    }

    if options.mode == "action" and next_step is not None:
        next_step_guidance = compose_next_step_guidance(
            next_step, NextStepComposeOptions(requested_action=options.action)
        )
        kwargs["next_step"] = {**next_step, "guidance": next_step_guidance}
    elif options.mode == "check":
        kwargs["summary"] = compose_check_summary(
            CheckSummaryComposeInput(
                context=context,
                findings=all_findings,
                consider_justification_rejection=consider_justification_rejection,
            )
        )

    return AssayResult(**kwargs)


def _run_check(
    check_type: AssayCheckType,
    context: AssayContext,
    generate_id: IdGenerator,
    run_options: CheckRunOptions,
) -> CheckOutput:
    cfg = run_options.config["checks"][check_type]
    if not cfg["enabled"]:
        return CheckOutput(findings=[], progress=neutral_progress())
    fn = CHECK_REGISTRY[check_type]
    return fn(context, generate_id, run_options)


def _group_by_check(findings: list[Finding]) -> dict[AssayCheckType, list[Finding]]:
    out: dict[AssayCheckType, list[Finding]] = {
        "acceptance-coverage": [],
        "implementation-coverage": [],
        "file-action-coverage": [],
        "test-result-presence": [],
    }
    for f in findings:
        out[f.check_type].append(f)
    return out


def _to_check_result(
    check_type: AssayCheckType,
    findings: list[Finding],
    progress: CheckProgress,
) -> CheckResult:
    passed = not any(f.severity == "error" for f in findings)
    return CheckResult(check_type=check_type, passed=passed, findings=findings, progress=progress)


def _dispatch_verbosity(
    finding: Finding,
    mode: AssayMode,
    anchor_entity_id: str | None,
) -> GuidanceVerbosity:
    if mode == "check":
        return "compact"
    if anchor_entity_id is None:
        return "compact"
    if finding.primary_entity_id == anchor_entity_id:
        return "verbose"
    if anchor_entity_id in finding.entity_ids:
        return "verbose"
    return "compact"


def _resolve_anchor_entity_id(step: dict[str, Any]) -> str | None:
    if step["reason"] == "complete":
        return None
    action = step["action"]
    if action == "check-imp-step":
        return str(step["implStep"]["id"])
    if action == "check-ac":
        return str(step["acceptanceCriterion"]["id"])
    if action == "add-files-changes":
        if step["reason"] == "resolve":
            issues = step["issues"]
            return str(issues[0]["fileChange"]["id"]) if issues else None
        targets = step["targets"]
        return str(targets[0]["expectedPath"]) if targets else None
    if action == "add-test-results":
        if step["reason"] == "resolve":
            issues = step["issues"]
            return str(issues[0]["testResult"]["id"]) if issues else None
        targets = step["targets"]
        return str(targets[0]["testType"]) if targets else None
    return None


def _now_iso() -> str:
    now = datetime.now(UTC)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"
