"""Complete next-step template (port of ``templates/next-steps/complete.ts``)."""

from __future__ import annotations

from typing import Any

from .template_types import NextStepTemplateOutput

_COMPLETE = """Work session is ready for closure.

 Summary:
 - Total satisfied items: {totalCompleted} of {totalTotal}

 No pending items, no blocking issues. The work session has successfully
 covered every applicable action.

 Recommended move:
 1. Invoke complete_work_session to formally close the session"""


def complete_dispatcher(step: dict[str, Any]) -> NextStepTemplateOutput:
    if step["reason"] != "complete":
        raise ValueError("completeDispatcher: invalid step")
    return {
        "template": _COMPLETE,
        "context": {
            "totalCompleted": step["progress"]["completed"],
            "totalTotal": step["progress"]["total"],
        },
        "operations": ["complete_work_session"],
    }
