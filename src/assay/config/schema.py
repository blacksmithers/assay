"""Config schema validation (port of ``config/schema.ts``).

The TS source uses a strict Zod schema. Here we validate the plain ``dict``
config: the top-level object is **strict** (unknown keys are rejected, like
``.strict()``), while the nested check objects **strip** unknown keys (plain
``z.object`` behaviour). ``version`` must be the literal ``1``.
"""

from __future__ import annotations

from typing import Any

from ..runtime.types.config import AssayforgeConfig
from .safe_ranges import ConfigValidationError

_SEVERITIES = ("error", "warn", "off")
_CHECK_NAMES = (
    "acceptance-coverage",
    "implementation-coverage",
    "file-action-coverage",
    "test-result-presence",
)
_BASE_FIELDS = ("enabled", "severity")
_FAC_FIELDS = (
    *_BASE_FIELDS,
    "pendingJustificationSeverity",
    "rejectedJustificationSeverity",
)
_TRP_FIELDS = (
    *_BASE_FIELDS,
    "skippedWithoutJustificationSeverity",
    "testsFailingSeverity",
    "failureJustificationRejectedSeverity",
    "skipJustificationRejectedSeverity",
)
_CHECK_FIELDS = {
    "acceptance-coverage": _BASE_FIELDS,
    "implementation-coverage": _BASE_FIELDS,
    "file-action-coverage": _FAC_FIELDS,
    "test-result-presence": _TRP_FIELDS,
}


def _require_severity(obj: dict[str, Any], field: str, path: str) -> str:
    value = obj.get(field)
    if value not in _SEVERITIES:
        raise ConfigValidationError(f"{path}.{field}: invalid severity {value!r}")
    return str(value)


def _validate_check(raw: Any, name: str) -> dict[str, Any]:
    path = f"checks.{name}"
    if not isinstance(raw, dict):
        raise ConfigValidationError(f"{path}: expected object")
    if not isinstance(raw.get("enabled"), bool):
        raise ConfigValidationError(f"{path}.enabled: expected boolean")
    out: dict[str, Any] = {}
    for field in _CHECK_FIELDS[name]:
        if field == "enabled":
            out["enabled"] = raw["enabled"]
        else:
            out[field] = _require_severity(raw, field, path)
    return out


def validate_config(raw: Any) -> AssayforgeConfig:
    """Validate a full config (mirror of ``AssayforgeConfigSchema.parse``)."""
    if not isinstance(raw, dict):
        raise ConfigValidationError("config: expected object")
    extra = set(raw) - {"version", "checks"}
    if extra:
        raise ConfigValidationError(f"config: unrecognized key(s) {sorted(extra)}")
    # z.literal(1): strict ``=== 1``. JS distinguishes ``true`` from ``1`` (so
    # reject booleans) but treats ``1.0 === 1`` (so a float 1.0 is accepted).
    version = raw.get("version")
    if isinstance(version, bool) or version != 1:
        raise ConfigValidationError("config.version: must be the literal 1")
    checks = raw.get("checks")
    if not isinstance(checks, dict):
        raise ConfigValidationError("config.checks: expected object")
    missing = set(_CHECK_NAMES) - set(checks)
    if missing:
        raise ConfigValidationError(f"config.checks: missing {sorted(missing)}")

    out_checks: dict[str, Any] = {}
    for name in _CHECK_NAMES:
        out_checks[name] = _validate_check(checks[name], name)
    return {"version": 1, "checks": out_checks}


class _AssayforgeConfigSchema:
    """Zod-like wrapper exposing ``.parse`` / ``.safe_parse`` for API parity."""

    def parse(self, raw: Any) -> AssayforgeConfig:
        return validate_config(raw)

    def safe_parse(self, raw: Any) -> tuple[bool, AssayforgeConfig | None]:
        try:
            return True, validate_config(raw)
        except ConfigValidationError:
            return False, None


AssayforgeConfigSchema = _AssayforgeConfigSchema()
