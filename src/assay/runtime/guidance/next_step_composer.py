"""Next-step-guidance composer (port of ``guidance/next-step-composer.ts``)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .interpolate import interpolate
from .templates.next_steps import next_step_key, next_step_templates


@dataclass
class NextStepComposeOptions:
    requested_action: str | None = None


def compose_next_step_guidance(
    step: dict[str, Any],
    options: NextStepComposeOptions | None = None,
) -> dict[str, Any]:
    options = options or NextStepComposeOptions()
    key = next_step_key(step)
    dispatcher = next_step_templates[key]
    out = dispatcher(step)
    ctx: dict[str, Any] = dict(out["context"])
    if options.requested_action is not None:
        ctx["requestedAction"] = options.requested_action
    message = interpolate(out["template"], ctx)
    return {"message": message, "operations": list(out["operations"])}
