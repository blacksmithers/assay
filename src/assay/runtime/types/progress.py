"""Check progress contract (port of ``runtime/types/progress.ts``)."""

from __future__ import annotations

from ._base import CamelModel


class CheckProgress(CamelModel):
    total: int
    completed: int
    remaining: int
    remaining_ids: list[str]
    next_in_order_id: str | None = None
