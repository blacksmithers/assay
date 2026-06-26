"""Next-step contract (port of ``runtime/types/next-step.ts``).

The next-step value is assembled as a plain ordered ``dict`` (mirroring the TS
discriminated-union object literal) so that embedded input rows
(``issues[].fileChange`` etc.) carry their zod-faithful serialization. The
``NextStep`` alias documents that shape; ``reason`` is one of
:data:`NextStepReason`.
"""

from __future__ import annotations

from typing import Any, Literal

NextStepReason = Literal[
    "continue",
    "next-action",
    "resolve",
    "prerequisite",
    "complete",
]

# Assembled object literal; keys depend on (reason, action).
NextStep = dict[str, Any]


class NextStepGuidance(dict[str, Any]):
    """A ``{"message": str, "operations": list[str]}`` mapping."""
