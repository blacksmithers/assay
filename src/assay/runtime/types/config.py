"""Config types (port of ``runtime/types/config.ts``).

The runtime config is a plain nested ``dict`` mirroring the TS object literal —
the engine reads it by string key (``config["checks"]["acceptance-coverage"]``),
exactly as the TS source does. ``TypedDict`` shapes document the structure of the
well-formed sub-objects.
"""

from __future__ import annotations

from typing import Any, Literal

from typing_extensions import TypedDict

SeverityOverride = Literal["error", "warn", "off"]


class CheckBaseConfig(TypedDict):
    enabled: bool
    severity: SeverityOverride


class FileActionCoverageConfig(CheckBaseConfig):
    pendingJustificationSeverity: SeverityOverride
    rejectedJustificationSeverity: SeverityOverride


class TestResultPresenceConfig(CheckBaseConfig):
    skippedWithoutJustificationSeverity: SeverityOverride
    testsFailingSeverity: SeverityOverride
    failureJustificationRejectedSeverity: SeverityOverride
    skipJustificationRejectedSeverity: SeverityOverride


# Runtime config: a loose mapping, read by string key like the TS object literal.
AssayforgeConfig = dict[str, Any]
