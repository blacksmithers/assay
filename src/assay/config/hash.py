"""Config hashing (port of ``config/hash.ts``).

``configHash`` = ``cfg-<hex>`` of a Java-style 31-multiply string hash over the
canonical (recursively key-sorted) ``JSON.stringify`` of the config — byte-for-byte
identical to the TS implementation.
"""

from __future__ import annotations

import json

from ..runtime.types.config import AssayforgeConfig


def config_hash(config: AssayforgeConfig) -> str:
    # canonicalize: recursive key sort, no whitespace (JSON.stringify default).
    payload = json.dumps(config, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    h = 0
    for ch in payload:
        # h = (h * 31 + charCode) | 0  — kept in the unsigned 32-bit residue class,
        # which equals the JS signed-int result modulo 2**32.
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return f"cfg-{h:x}"
