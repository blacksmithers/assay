"""assay config — defaults, schema, merge, hash, loader (port of ``config/``)."""

from __future__ import annotations

from .defaults import HARDCODED_DEFAULTS
from .hash import config_hash
from .loader import load_config, load_defaults
from .merge import DeepPartial, merge_config
from .safe_ranges import SAFE_RANGES, ConfigValidationError, validate_safe_ranges
from .schema import AssayforgeConfigSchema, validate_config

__all__ = [
    "HARDCODED_DEFAULTS",
    "SAFE_RANGES",
    "AssayforgeConfigSchema",
    "ConfigValidationError",
    "DeepPartial",
    "config_hash",
    "load_config",
    "load_defaults",
    "merge_config",
    "validate_config",
    "validate_safe_ranges",
]
