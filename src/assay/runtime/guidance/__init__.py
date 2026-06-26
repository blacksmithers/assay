"""Guidance composition (port of ``guidance/index.ts``)."""

from __future__ import annotations

from .check_summary_composer import CheckSummaryComposeInput, compose_check_summary
from .finding_composer import GuidanceVerbosity, compose_finding_guidance
from .interpolate import interpolate
from .next_step_composer import NextStepComposeOptions, compose_next_step_guidance
from .templates.findings import finding_templates
from .templates.next_steps import NextStepTemplateKey, next_step_key, next_step_templates

__all__ = [
    "CheckSummaryComposeInput",
    "GuidanceVerbosity",
    "NextStepComposeOptions",
    "NextStepTemplateKey",
    "compose_check_summary",
    "compose_finding_guidance",
    "compose_next_step_guidance",
    "finding_templates",
    "interpolate",
    "next_step_key",
    "next_step_templates",
]
