"""Action applicability (port of ``next-step/applicability.ts``)."""

from __future__ import annotations

from ..enums import ASSAY_ACTION_SEQUENCE, AssayAction
from ..field_declarations import is_field_na
from ..types.context import Ticket


def action_applies(ticket: Ticket, action: AssayAction) -> bool:
    if action == "check-imp-step":
        if is_field_na(ticket, "implementationSteps"):
            return False
        return len(ticket.implementation_steps) > 0
    if action == "check-ac":
        if is_field_na(ticket, "acceptanceCriteria"):
            return False
        return len(ticket.acceptance_criteria) > 0
    if action == "add-files-changes":
        all_na = (
            is_field_na(ticket, "filesToBeCreated")
            and is_field_na(ticket, "filesToBeModified")
            and is_field_na(ticket, "filesToBeDeleted")
            and is_field_na(ticket, "filesToBeReferenced")
        )
        if all_na:
            return False
        has_any = (
            (not is_field_na(ticket, "filesToBeCreated") and len(ticket.files_to_be_created) > 0)
            or (not is_field_na(ticket, "filesToBeModified") and len(ticket.files_to_be_modified) > 0)
            or (not is_field_na(ticket, "filesToBeDeleted") and len(ticket.files_to_be_deleted) > 0)
            or (
                not is_field_na(ticket, "filesToBeReferenced")
                and len(ticket.files_to_be_referenced) > 0
            )
        )
        return has_any
    if action == "add-test-results":
        if is_field_na(ticket, "testSpecification"):
            return False
        spec = ticket.test_specification
        if spec is None:
            return False
        return len(spec.test_types) > 0
    return False


def applicable_actions(ticket: Ticket) -> list[AssayAction]:
    return [action for action in ASSAY_ACTION_SEQUENCE if action_applies(ticket, action)]
