"""Neutral (zero) progress (port of ``progress/neutral.ts``)."""

from __future__ import annotations

from ..types.progress import CheckProgress


def neutral_progress() -> CheckProgress:
    return CheckProgress(total=0, completed=0, remaining=0, remaining_ids=[])


NEUTRAL_PROGRESS: CheckProgress = neutral_progress()
