"""Config loading (port of ``config/loader.ts``)."""

from __future__ import annotations

from copy import deepcopy
from importlib import resources
from typing import Any

import yaml

from ..runtime.types.config import AssayforgeConfig
from .defaults import HARDCODED_DEFAULTS
from .merge import DeepPartial, merge_config
from .safe_ranges import validate_safe_ranges
from .schema import validate_config


def load_defaults() -> AssayforgeConfig:
    """Load the canonical default config from the packaged ``defaults.yml``.

    Validated through the schema + safe ranges; falls back to
    :data:`HARDCODED_DEFAULTS` if the packaged YAML is missing or invalid.
    """
    try:
        raw = (
            resources.files("assay.config.data")
            .joinpath("defaults.yml")
            .read_text(encoding="utf-8")
        )
        parsed: Any = yaml.safe_load(raw)
        validated = validate_config(parsed)
        validate_safe_ranges(validated)
        return validated
    except Exception:
        return deepcopy(HARDCODED_DEFAULTS)


def load_config(override: DeepPartial | None = None) -> AssayforgeConfig:
    defaults = load_defaults()
    if not override:
        return defaults
    return merge_config(defaults, override)
