"""Shared Pydantic bases for assay contracts.

Two bases, because *output* and *input* contracts serialize with different
``JSON.stringify`` semantics in the TS engine:

* :class:`CamelModel` — engine **output** contracts (``Finding``, ``CheckResult``,
  ``AssayResult`` …). snake_case attributes with auto camelCase aliases,
  serialized via ``model_dump(mode="json", by_alias=True, exclude_unset=True)``.
  ``exclude_unset`` mirrors ``JSON.stringify``: omit ``undefined`` (fields never
  set), keep ``null`` (fields explicitly set to ``None``).

* :class:`InputModel` — work-session / spec **input** contracts (the
  zod-inferred ``WorkSession*`` / ``Ticket`` shapes). Unknown keys are ignored
  (zod strips them). :meth:`InputModel.to_input_dict` reproduces a zod-parsed
  object: defaults applied **and kept**, optional-absent fields **omitted**
  (``exclude_none``). Used when the engine embeds an input row into its output
  (e.g. ``nextStep.issues[].fileChange``).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )

    def to_json_dict(self) -> dict[str, Any]:
        """Canonical camelCase JSON dict (TS ``JSON.stringify`` semantics)."""
        return self.model_dump(mode="json", by_alias=True, exclude_unset=True)


class InputModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
    )

    def to_input_dict(self) -> dict[str, Any]:
        """zod-parse-equivalent JSON dict.

        Defaults are kept; an optional field that was never provided is omitted
        (JS ``undefined``); a field explicitly set to ``None`` is kept as
        ``null`` (JS distinguishes ``undefined`` from ``null`` — e.g. a
        ``z.unknown().optional()`` field such as ``suites`` accepts an explicit
        ``null``). So drop a ``None`` value only when its field is not in
        ``model_fields_set``.
        """
        full = self.model_dump(mode="json", by_alias=True)
        set_aliases: set[str] = set()
        for name in self.model_fields_set:
            field = type(self).model_fields.get(name)
            alias = field.alias if field is not None and field.alias else name
            set_aliases.add(alias)
        return {k: v for k, v in full.items() if v is not None or k in set_aliases}
