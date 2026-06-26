"""Hardcoded default config (verbatim port of ``config/defaults.ts``).

Fallback used by :func:`assay.config.loader.load_defaults` when the packaged
``defaults.yml`` is unreadable.
"""

from __future__ import annotations

from ..runtime.types.config import AssayforgeConfig

HARDCODED_DEFAULTS: AssayforgeConfig = {
    "version": 1,
    "checks": {
        "acceptance-coverage": {
            "enabled": True,
            "severity": "error",
        },
        "implementation-coverage": {
            "enabled": True,
            "severity": "error",
        },
        "file-action-coverage": {
            "enabled": True,
            "severity": "error",
            "pendingJustificationSeverity": "warn",
            "rejectedJustificationSeverity": "error",
        },
        "test-result-presence": {
            "enabled": True,
            "severity": "error",
            "skippedWithoutJustificationSeverity": "error",
            "testsFailingSeverity": "error",
            "failureJustificationRejectedSeverity": "error",
            "skipJustificationRejectedSeverity": "error",
        },
    },
}
