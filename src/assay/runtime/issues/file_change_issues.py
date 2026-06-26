"""Open file-change issue detection (port of ``issues/file-change-issues.ts``)."""

from __future__ import annotations

from dataclasses import dataclass

from ..types.context import AssayContext, WorkSessionFileChange
from ..types.issues import FileChangeIssue


@dataclass
class FileChangeIssueEntry:
    file_change: WorkSessionFileChange
    issue: FileChangeIssue


def find_open_file_change_issues(
    context: AssayContext,
    consider_justification_rejection: bool,
) -> list[FileChangeIssueEntry]:
    issues: list[FileChangeIssueEntry] = []

    for fc in context.file_changes:
        if fc.status == "matched":
            continue

        has_justification = bool(fc.justification)
        approved = fc.justification_approved

        if not has_justification:
            if fc.status == "missing":
                issues.append(FileChangeIssueEntry(fc, "missing-without-justification"))
            elif fc.status == "mismatched":
                issues.append(FileChangeIssueEntry(fc, "mismatched-without-justification"))
            elif fc.status == "extra":
                issues.append(FileChangeIssueEntry(fc, "extra-without-justification"))
            continue

        if approved == "rejected" and consider_justification_rejection:
            issues.append(FileChangeIssueEntry(fc, "justification-rejected"))
        # 'pending' / 'approved' do not surface as issues

    issues.sort(key=lambda e: e.file_change.recorded_at)
    return issues
