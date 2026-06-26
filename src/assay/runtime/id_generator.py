"""Finding ID generators (port of ``runtime/id-generator.ts``).

``IdGenerator`` receives the finding-without-``id`` (as a mapping with the TS
camelCase keys) and returns a stable string id.

* :func:`uuid_id_generator` — random UUID (production default).
* :func:`deterministic_id_generator` — sha256 over a canonical seed, used by the
  differential surface so ids are stable across runs.

The deterministic seed reproduces the TS ``JSON.stringify`` byte-for-byte:
insertion-ordered keys, ``undefined`` keys omitted, no whitespace.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Callable, Mapping
from typing import Any

IdGenerator = Callable[[Mapping[str, Any]], str]


def _utf16_key(value: str) -> bytes:
    # JS Array.prototype.sort() with no comparator orders strings by UTF-16
    # code unit. Comparing big-endian UTF-16 byte sequences reproduces that
    # ordering (including surrogate-pair placement for supplementary-plane
    # characters), whereas Python's default sort uses code points.
    return value.encode("utf-16-be")


def uuid_id_generator(_finding: Mapping[str, Any]) -> str:
    return str(uuid.uuid4())


def deterministic_id_generator(finding: Mapping[str, Any]) -> str:
    seed: dict[str, Any] = {
        "checkType": finding["checkType"],
        "severity": finding["severity"],
    }
    primary = finding.get("primaryEntityId")
    if primary is not None:
        seed["primaryEntityId"] = primary
    seed["entityIds"] = sorted(finding["entityIds"], key=_utf16_key)
    related = finding.get("relatedEntityIds")
    if related is not None:
        seed["relatedEntityIds"] = sorted(related, key=_utf16_key)
    context = finding.get("context")
    if context is not None:
        seed["context"] = context
    payload = json.dumps(seed, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
