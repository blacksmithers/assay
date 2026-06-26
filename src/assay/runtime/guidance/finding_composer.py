"""Finding-guidance composer (port of ``guidance/finding-composer.ts``)."""

from __future__ import annotations

from typing import Literal

from ..types.finding import Finding, FindingGuidance
from .interpolate import interpolate
from .templates.findings import finding_templates

GuidanceVerbosity = Literal["compact", "verbose"]


def compose_finding_guidance(finding: Finding, verbosity: GuidanceVerbosity) -> FindingGuidance:
    dispatcher = finding_templates[finding.check_type]
    ctx = finding.context or {}
    tpl = dispatcher(ctx)
    template = tpl["compact"] if verbosity == "compact" else tpl["verbose"]
    message = interpolate(template, ctx)
    return FindingGuidance(message=message, operations=list(tpl["operations"]))
