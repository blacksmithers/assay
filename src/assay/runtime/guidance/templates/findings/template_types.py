"""Finding-template shapes (port of ``templates/findings/template-types.ts``)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from typing_extensions import TypedDict

from ....operations_registry import OperationName


class FindingTemplate(TypedDict):
    compact: str
    verbose: str
    operations: list[OperationName]


FindingTemplateDispatcher = Callable[[dict[str, Any]], FindingTemplate]
