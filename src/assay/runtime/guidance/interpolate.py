"""Template interpolation (port of ``guidance/interpolate.ts``).

Replaces ``{word}`` with ``ctx[word]`` rendered the way JS ``String(value)``
would (booleans become ``true``/``false``); ``undefined``/``null`` (missing key
or ``None``) renders the literal ``<word>``.
"""

from __future__ import annotations

import re
from typing import Any

_PATTERN = re.compile(r"\{(\w+)\}")


def _js_str(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def interpolate(template: str, ctx: dict[str, Any]) -> str:
    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        value = ctx.get(key)
        if value is None:
            return f"<{key}>"
        return _js_str(value)

    return _PATTERN.sub(_replace, template)
