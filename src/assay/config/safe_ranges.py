"""Safe-range validation (port of ``config/safe-ranges.ts``)."""

from __future__ import annotations

from typing import Any

from ..runtime.types.config import AssayforgeConfig, SeverityOverride

_SEVERITY_VALUES: tuple[SeverityOverride, ...] = ("error", "warn", "off")

SAFE_RANGES: dict[str, dict[str, Any]] = {
    "checks.*.enabled": {"type": "boolean"},
    "checks.*.severity": {"enum": list(_SEVERITY_VALUES)},
    "checks.file-action-coverage.pendingJustificationSeverity": {"enum": list(_SEVERITY_VALUES)},
    "checks.file-action-coverage.rejectedJustificationSeverity": {"enum": list(_SEVERITY_VALUES)},
    "checks.test-result-presence.skippedWithoutJustificationSeverity": {
        "enum": list(_SEVERITY_VALUES)
    },
    "checks.test-result-presence.testsFailingSeverity": {"enum": list(_SEVERITY_VALUES)},
    "checks.test-result-presence.failureJustificationRejectedSeverity": {
        "enum": list(_SEVERITY_VALUES)
    },
    "checks.test-result-presence.skipJustificationRejectedSeverity": {
        "enum": list(_SEVERITY_VALUES)
    },
}


class ConfigValidationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.name = "ConfigValidationError"


def _js_typeof(value: Any) -> str:
    # Reproduce JS ``typeof`` so error messages match the TS engine byte-for-byte.
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if value is None:
        return "undefined"
    return "object"


def _js_string(value: Any) -> str:
    # Reproduce JS ``String(value)`` for the values that reach these messages.
    if value is None:
        return "undefined"
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def _ensure_severity(path: str, value: Any) -> None:
    if value not in _SEVERITY_VALUES:
        raise ConfigValidationError(
            f"{path} must be one of [{', '.join(_SEVERITY_VALUES)}], got {_js_string(value)}"
        )


def validate_safe_ranges(config: AssayforgeConfig) -> None:
    for check_name, check in config["checks"].items():
        if not isinstance(check.get("enabled"), bool):
            raise ConfigValidationError(
                f"checks.{check_name}.enabled must be boolean, "
                f"got {_js_typeof(check.get('enabled'))}"
            )
        if check.get("severity") not in _SEVERITY_VALUES:
            raise ConfigValidationError(
                f"checks.{check_name}.severity must be one of "
                f"[{', '.join(_SEVERITY_VALUES)}], got {_js_string(check.get('severity'))}"
            )

    fac = config["checks"]["file-action-coverage"]
    _ensure_severity(
        "checks.file-action-coverage.pendingJustificationSeverity",
        fac.get("pendingJustificationSeverity"),
    )
    _ensure_severity(
        "checks.file-action-coverage.rejectedJustificationSeverity",
        fac.get("rejectedJustificationSeverity"),
    )

    trp = config["checks"]["test-result-presence"]
    _ensure_severity(
        "checks.test-result-presence.skippedWithoutJustificationSeverity",
        trp.get("skippedWithoutJustificationSeverity"),
    )
    _ensure_severity(
        "checks.test-result-presence.testsFailingSeverity",
        trp.get("testsFailingSeverity"),
    )
    _ensure_severity(
        "checks.test-result-presence.failureJustificationRejectedSeverity",
        trp.get("failureJustificationRejectedSeverity"),
    )
    _ensure_severity(
        "checks.test-result-presence.skipJustificationRejectedSeverity",
        trp.get("skipJustificationRejectedSeverity"),
    )
