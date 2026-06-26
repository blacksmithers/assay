"""Next-step template dispatch (port of ``templates/next-steps/index.ts``)."""

from __future__ import annotations

from typing import Any, Literal

from .complete import complete_dispatcher
from .continue_ import (
    continue_ac_dispatcher,
    continue_files_dispatcher,
    continue_imp_step_dispatcher,
    continue_tests_dispatcher,
)
from .prerequisite import (
    prerequisite_ac_dispatcher,
    prerequisite_files_dispatcher,
    prerequisite_imp_step_dispatcher,
    prerequisite_tests_dispatcher,
)
from .resolve import resolve_files_dispatcher, resolve_tests_dispatcher
from .template_types import NextStepTemplateDispatcher, NextStepTemplateOutput

NextStepTemplateKey = Literal[
    "continue::check-imp-step",
    "continue::check-ac",
    "continue::add-files-changes",
    "continue::add-test-results",
    "next-action::check-imp-step",
    "next-action::check-ac",
    "next-action::add-files-changes",
    "next-action::add-test-results",
    "resolve::add-files-changes",
    "resolve::add-test-results",
    "prerequisite::check-imp-step",
    "prerequisite::check-ac",
    "prerequisite::add-files-changes",
    "prerequisite::add-test-results",
    "complete",
]

next_step_templates: dict[str, NextStepTemplateDispatcher] = {
    "continue::check-imp-step": continue_imp_step_dispatcher,
    "continue::check-ac": continue_ac_dispatcher,
    "continue::add-files-changes": continue_files_dispatcher,
    "continue::add-test-results": continue_tests_dispatcher,
    "next-action::check-imp-step": continue_imp_step_dispatcher,
    "next-action::check-ac": continue_ac_dispatcher,
    "next-action::add-files-changes": continue_files_dispatcher,
    "next-action::add-test-results": continue_tests_dispatcher,
    "resolve::add-files-changes": resolve_files_dispatcher,
    "resolve::add-test-results": resolve_tests_dispatcher,
    "prerequisite::check-imp-step": prerequisite_imp_step_dispatcher,
    "prerequisite::check-ac": prerequisite_ac_dispatcher,
    "prerequisite::add-files-changes": prerequisite_files_dispatcher,
    "prerequisite::add-test-results": prerequisite_tests_dispatcher,
    "complete": complete_dispatcher,
}


def next_step_key(step: dict[str, Any]) -> str:
    if step["reason"] == "complete":
        return "complete"
    return f"{step['reason']}::{step['action']}"


__all__ = [
    "NextStepTemplateDispatcher",
    "NextStepTemplateKey",
    "NextStepTemplateOutput",
    "complete_dispatcher",
    "continue_ac_dispatcher",
    "continue_files_dispatcher",
    "continue_imp_step_dispatcher",
    "continue_tests_dispatcher",
    "next_step_key",
    "next_step_templates",
    "prerequisite_ac_dispatcher",
    "prerequisite_files_dispatcher",
    "prerequisite_imp_step_dispatcher",
    "prerequisite_tests_dispatcher",
    "resolve_files_dispatcher",
    "resolve_tests_dispatcher",
]
