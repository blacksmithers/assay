"""Action enums (port of ``runtime/enums.ts``)."""

from __future__ import annotations

from typing import Literal

AssayAction = Literal[
    "check-imp-step",
    "add-test-results",
    "add-files-changes",
    "check-ac",
]

ASSAY_ACTIONS: tuple[AssayAction, ...] = (
    "check-imp-step",
    "add-test-results",
    "add-files-changes",
    "check-ac",
)

ASSAY_ACTION_SEQUENCE: tuple[AssayAction, ...] = (
    "check-imp-step",
    "add-test-results",
    "add-files-changes",
    "check-ac",
)
