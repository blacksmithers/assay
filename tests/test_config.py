"""Config parity: defaults, hash, merge, schema validation."""

from __future__ import annotations

import pytest

from assay import (
    HARDCODED_DEFAULTS,
    ConfigValidationError,
    config_hash,
    load_defaults,
    merge_config,
    validate_config,
)


def test_packaged_defaults_match_hardcoded() -> None:
    assert load_defaults() == HARDCODED_DEFAULTS


def test_default_config_hash_matches_reference() -> None:
    # Captured from the reference TS engine (snapshot meta.configHash).
    assert config_hash(load_defaults()) == "cfg-e5e5b8b6"


def test_config_hash_is_key_order_independent() -> None:
    a = {"version": 1, "checks": HARDCODED_DEFAULTS["checks"]}
    b = {"checks": HARDCODED_DEFAULTS["checks"], "version": 1}
    assert config_hash(a) == config_hash(b)


def test_config_hash_changes_with_config() -> None:
    changed = merge_config(
        load_defaults(), {"checks": {"acceptance-coverage": {"severity": "warn"}}}
    )
    assert config_hash(changed) != config_hash(load_defaults())


def test_merge_overrides_and_revalidates() -> None:
    merged = merge_config(
        load_defaults(), {"checks": {"test-result-presence": {"enabled": False}}}
    )
    assert merged["checks"]["test-result-presence"]["enabled"] is False
    # Untouched checks preserved.
    assert merged["checks"]["acceptance-coverage"]["severity"] == "error"
    # Inputs are not mutated.
    assert load_defaults()["checks"]["test-result-presence"]["enabled"] is True


def test_merge_rejects_invalid_severity() -> None:
    with pytest.raises(ConfigValidationError):
        merge_config(load_defaults(), {"checks": {"acceptance-coverage": {"severity": "boom"}}})


def test_validate_rejects_unknown_top_level_key() -> None:
    bad = {**load_defaults(), "extra": 1}
    with pytest.raises(ConfigValidationError):
        validate_config(bad)


def test_validate_rejects_wrong_version() -> None:
    bad = {**load_defaults(), "version": 2}
    with pytest.raises(ConfigValidationError):
        validate_config(bad)
