"""Implementation-coverage finding templates (port of ``findings/implementation-coverage.ts``)."""

from __future__ import annotations

from typing import Any

from .template_types import FindingTemplate

_COMPACT = """Implementation step #{order} not completed.
 - {text}

 Execute the step, then run mark_implementation_step_completion."""

_VERBOSE = """Implementation step has not been completed yet.
 - Position: {order} of {progressTotal}
 - Progress: {progressCompleted} done, {progressRemaining} remaining
 - Description: {text}

 Implementation steps are the spec's instructions for what to build.
 Each step must be marked done before the work session can complete.

 Possible reasons this is pending:
 - You completed the work but have not registered the completion
 - You haven't started the work for this step
 - The step is no longer relevant given decisions made during implementation

 Recommended moves:
 1. Execute the step as described
 2. Run mark_implementation_step_completion with done=true once completed
 3. If the step is no longer required, reopen the planning session to remove it"""


def implementation_coverage_dispatcher(_ctx: dict[str, Any]) -> FindingTemplate:
    return {
        "compact": _COMPACT,
        "verbose": _VERBOSE,
        "operations": ["mark_implementation_step_completion"],
    }
