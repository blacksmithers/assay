"""assay runtime — the engine, its checks, next-step resolver, and guidance."""

from __future__ import annotations

from .assay import assay
from .version import ENGINE_VERSION

__all__ = ["ENGINE_VERSION", "assay"]
