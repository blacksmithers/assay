"""File-action progress + declared-file collection (port of ``progress/file-action.ts``)."""

from __future__ import annotations

from dataclasses import dataclass

from ..field_declarations import is_field_na
from ..types.context import AssayContext, ExpectedAction, Ticket
from ..types.progress import CheckProgress
from .neutral import neutral_progress


@dataclass(frozen=True)
class DeclaredFile:
    expected_path: str
    expected_action: ExpectedAction


# action -> (camelCase field path used for N/A declarations, snake_case attribute)
_FILE_FIELDS: dict[ExpectedAction, tuple[str, str]] = {
    "create": ("filesToBeCreated", "files_to_be_created"),
    "modify": ("filesToBeModified", "files_to_be_modified"),
    "delete": ("filesToBeDeleted", "files_to_be_deleted"),
    "reference": ("filesToBeReferenced", "files_to_be_referenced"),
}


def collect_declared_files(ticket: Ticket) -> list[DeclaredFile]:
    out: list[DeclaredFile] = []
    for action in ("create", "modify", "delete", "reference"):
        field, attr = _FILE_FIELDS[action]
        if is_field_na(ticket, field):
            continue
        for path in getattr(ticket, attr):
            out.append(DeclaredFile(expected_path=path, expected_action=action))
    return out


def all_files_na(ticket: Ticket) -> bool:
    return (
        is_field_na(ticket, "filesToBeCreated")
        and is_field_na(ticket, "filesToBeModified")
        and is_field_na(ticket, "filesToBeDeleted")
        and is_field_na(ticket, "filesToBeReferenced")
    )


def compute_file_action_progress(context: AssayContext) -> CheckProgress:
    ticket = context.ticket
    file_changes = context.file_changes
    if all_files_na(ticket):
        return neutral_progress()

    declared = collect_declared_files(ticket)
    extras = [fc for fc in file_changes if fc.status == "extra"]

    total = len(declared) + len(extras)
    if total == 0:
        return neutral_progress()

    remaining_ids: list[str] = []
    completed = 0

    # Declared expectations
    for d in declared:
        match = next(
            (
                fc
                for fc in file_changes
                if fc.expected_path == d.expected_path
                and fc.expected_action == d.expected_action
            ),
            None,
        )
        if match is None:
            remaining_ids.append(d.expected_path)
            continue
        is_matched = match.status == "matched"
        has_approved_just = bool(match.justification) and match.justification_approved == "approved"
        if is_matched or has_approved_just:
            completed += 1
        else:
            remaining_ids.append(d.expected_path)

    # Extras
    for extra in extras:
        has_approved_just = bool(extra.justification) and extra.justification_approved == "approved"
        if has_approved_just:
            completed += 1
        else:
            remaining_ids.append(extra.expected_path)

    remaining = total - completed
    return CheckProgress(
        total=total, completed=completed, remaining=remaining, remaining_ids=remaining_ids
    )
