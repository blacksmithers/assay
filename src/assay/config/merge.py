"""Config deep-merge (port of ``config/merge.ts``)."""

from __future__ import annotations

from typing import Any

from ..runtime.types.config import AssayforgeConfig
from .safe_ranges import ConfigValidationError, validate_safe_ranges
from .schema import validate_config

# A (possibly partial) override mapping. Mirrors the TS ``DeepPartial`` type.
DeepPartial = dict[str, Any]


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = dict(base)
    for key, override_val in override.items():
        base_val = base.get(key)
        if isinstance(override_val, dict) and isinstance(base_val, dict):
            out[key] = _deep_merge(base_val, override_val)
        else:
            # Every key present in the override is a real value. JS ``deepMerge``
            # only skips ``undefined``, which a Python dict cannot represent — an
            # explicit ``None`` is the analogue of JS ``null`` and replaces
            # wholesale (then fails schema validation, mirroring the TS engine).
            out[key] = override_val
    return out


def merge_config(base: AssayforgeConfig, *overrides: DeepPartial) -> AssayforgeConfig:
    """Deep-merge partial configs onto a base, then validate the result.

    Object fields merge recursively; arrays and primitives are replaced. Later
    overrides win. Inputs are not mutated.
    """
    result: dict[str, Any] = base
    for override in overrides:
        result = _deep_merge(result, override)
    try:
        validated = validate_config(result)
    except ConfigValidationError as exc:
        raise ConfigValidationError(
            f"Merged config failed schema validation: {exc}"
        ) from exc
    validate_safe_ranges(validated)
    return validated
