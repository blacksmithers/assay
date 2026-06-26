"""Check protocol + shared helpers (port of ``checks/types.ts``)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..id_generator import IdGenerator
from ..types.config import AssayforgeConfig
from ..types.context import AssayContext
from ..types.finding import AssayCheckType, Finding, FindingGuidance, FindingSeverity
from ..types.progress import CheckProgress


@dataclass
class CheckRunOptions:
    config: AssayforgeConfig
    consider_justification_rejection: bool


@dataclass
class CheckOutput:
    findings: list[Finding]
    progress: CheckProgress


CheckFn = Callable[[AssayContext, IdGenerator, "CheckRunOptions | None"], CheckOutput]


def placeholder_guidance() -> FindingGuidance:
    return FindingGuidance(message="", operations=[])


def make_finding(
    generate_id: IdGenerator,
    *,
    check_type: AssayCheckType,
    severity: FindingSeverity,
    message: str,
    primary_entity_id: str,
    entity_ids: list[str],
    context: dict[str, Any],
) -> Finding:
    """Compute the id from the finding seed, then build the placeholder finding."""
    seed = {
        "checkType": check_type,
        "severity": severity,
        "primaryEntityId": primary_entity_id,
        "entityIds": entity_ids,
        "context": context,
    }
    return Finding(
        id=generate_id(seed),
        check_type=check_type,
        severity=severity,
        message=message,
        primary_entity_id=primary_entity_id,
        entity_ids=entity_ids,
        context=context,
        guidance=placeholder_guidance(),
    )
