"""Next-step resolution (port of ``next-step/``)."""

from __future__ import annotations

from .applicability import action_applies, applicable_actions
from .resolver import resolve_next_step

__all__ = ["action_applies", "applicable_actions", "resolve_next_step"]
