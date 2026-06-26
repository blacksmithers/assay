"""Field N/A helper (port of ``runtime/field-declarations.ts``)."""

from __future__ import annotations

from .types.context import Ticket


def is_field_na(ticket: Ticket, field_path: str) -> bool:
    decls = ticket.field_declarations
    if not decls:
        return False
    entry = decls.get(field_path)
    return entry is not None and entry.value == "N/A"
