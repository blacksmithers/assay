"""Resolve templates + issue label/hint/op maps (port of ``templates/next-steps/resolve.ts``)."""

from __future__ import annotations

from typing import Any

from ....operations_registry import OperationName
from ....types.issues import FileChangeIssue, TestResultIssue
from .template_types import NextStepTemplateOutput

_RESOLVE_FILES = """File change issues require resolution before adding new entries.
 - Open issues: {issueCount}

{issuesList}

 Issues take priority over registering new file actions — assayforge prevents
 progress until each open issue is resolved. Address them in the order shown.

 Recommended moves:
 1. Resolve the first issue per its specific guidance (operations vary by issue type)
 2. Continue down the list; each resolution may surface the next pending action"""

_RESOLVE_TESTS = """Test result issues require resolution before adding new entries.
 - Open issues: {issueCount}

{issuesList}

 Issues take priority over registering new test types. Note: a later passing
 run for the same (testType, command) supersedes any older failing run for that
 pair, so re-running and recording a new result may auto-resolve some issues.

 Recommended moves:
 1. Resolve the first issue per its specific guidance
 2. For tests-failing issues, fixing and re-running with record_test_result auto-supersedes
 3. For skip/failure justifications, attach via add_skip_justification or add_failure_justification"""

FILE_ISSUE_LABEL: dict[FileChangeIssue, str] = {
    "missing-without-justification": "missing without justification",
    "mismatched-without-justification": "mismatched without justification",
    "extra-without-justification": "extra without justification",
    "justification-rejected": "justification rejected",
}

FILE_ISSUE_OPS: dict[FileChangeIssue, list[OperationName]] = {
    "missing-without-justification": ["record_file_change", "add_file_change_justification"],
    "mismatched-without-justification": ["record_file_change", "add_file_change_justification"],
    "extra-without-justification": ["add_file_change_justification"],
    "justification-rejected": ["record_file_change", "amend_file_change_justification"],
}

FILE_ISSUE_HINT: dict[FileChangeIssue, str] = {
    "missing-without-justification": (
        "register via record_file_change or attach add_file_change_justification"
    ),
    "mismatched-without-justification": (
        "correct via record_file_change or attach add_file_change_justification"
    ),
    "extra-without-justification": "declare via planning OR attach add_file_change_justification",
    "justification-rejected": "correct via record_file_change OR amend_file_change_justification",
}

TEST_ISSUE_LABEL: dict[TestResultIssue, str] = {
    "skipped-without-justification": "skipped without justification",
    "tests-failing": "tests failing without justification",
    "failure-justification-rejected": "failure justification rejected",
    "skip-justification-rejected": "skip justification rejected",
}

TEST_ISSUE_OPS: dict[TestResultIssue, list[OperationName]] = {
    "skipped-without-justification": ["record_test_result", "add_skip_justification"],
    "tests-failing": ["record_test_result", "add_failure_justification"],
    "failure-justification-rejected": ["record_test_result", "amend_failure_justification"],
    "skip-justification-rejected": ["record_test_result", "amend_skip_justification"],
}

TEST_ISSUE_HINT: dict[TestResultIssue, str] = {
    "skipped-without-justification": "attach via add_skip_justification",
    "tests-failing": "fix and re-run, OR add_failure_justification",
    "failure-justification-rejected": "fix the tests OR amend_failure_justification",
    "skip-justification-rejected": "run the tests OR amend_skip_justification",
}


def _dedupe_ops(lists: list[list[OperationName]]) -> list[OperationName]:
    seen: set[OperationName] = set()
    out: list[OperationName] = []
    for entries in lists:
        for op in entries:
            if op in seen:
                continue
            seen.add(op)
            out.append(op)
    return out


def resolve_files_dispatcher(step: dict[str, Any]) -> NextStepTemplateOutput:
    if step["reason"] != "resolve" or step["action"] != "add-files-changes":
        raise ValueError("resolveFilesDispatcher: invalid step")
    issues = step["issues"]
    if len(issues) == 0:
        issues_list = " - (none)"
    else:
        issues_list = "\n".join(
            f" - {i['fileChange']['expectedPath']} ({FILE_ISSUE_LABEL[i['issue']]}): "
            f"{FILE_ISSUE_HINT[i['issue']]}"
            for i in issues
        )
    operations = _dedupe_ops([FILE_ISSUE_OPS[i["issue"]] for i in issues])
    return {
        "template": _RESOLVE_FILES,
        "context": {"issueCount": len(issues), "issuesList": issues_list},
        "operations": operations,
    }


def resolve_tests_dispatcher(step: dict[str, Any]) -> NextStepTemplateOutput:
    if step["reason"] != "resolve" or step["action"] != "add-test-results":
        raise ValueError("resolveTestsDispatcher: invalid step")
    issues = step["issues"]
    if len(issues) == 0:
        issues_list = " - (none)"
    else:
        issues_list = "\n".join(
            f" - {i['testResult']['testType']} ({TEST_ISSUE_LABEL[i['issue']]}): "
            f"{TEST_ISSUE_HINT[i['issue']]}"
            for i in issues
        )
    operations = _dedupe_ops([TEST_ISSUE_OPS[i["issue"]] for i in issues])
    return {
        "template": _RESOLVE_TESTS,
        "context": {"issueCount": len(issues), "issuesList": issues_list},
        "operations": operations,
    }
