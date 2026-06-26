"""Finding contract (port of ``runtime/types/finding.ts``)."""

from __future__ import annotations

from typing import Any, Literal

from ._base import CamelModel

FindingSeverity = Literal["error", "warn"]

AssayCheckType = Literal[
    "acceptance-coverage",
    "implementation-coverage",
    "file-action-coverage",
    "test-result-presence",
]


class FindingGuidance(CamelModel):
    message: str
    operations: list[str]


class Finding(CamelModel):
    id: str
    check_type: AssayCheckType
    severity: FindingSeverity
    message: str
    primary_entity_id: str
    entity_ids: list[str]
    context: dict[str, Any] | None = None
    guidance: FindingGuidance
    related_entity_ids: list[str] | None = None
    tags: list[str] | None = None
