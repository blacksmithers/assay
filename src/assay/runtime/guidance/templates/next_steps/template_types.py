"""Next-step template shapes (port of ``templates/next-steps/template-types.ts``)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from typing_extensions import TypedDict

from ....operations_registry import OperationName


class NextStepTemplateOutput(TypedDict):
    template: str
    context: dict[str, Any]
    operations: list[OperationName]


NextStepTemplateDispatcher = Callable[[dict[str, Any]], NextStepTemplateOutput]
