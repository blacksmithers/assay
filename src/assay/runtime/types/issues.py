"""Issue-kind literals (port of ``runtime/types/issues.ts``)."""

from __future__ import annotations

from typing import Literal

FileChangeIssue = Literal[
    "missing-without-justification",
    "mismatched-without-justification",
    "extra-without-justification",
    "justification-rejected",
]

TestResultIssue = Literal[
    "skipped-without-justification",
    "tests-failing",
    "failure-justification-rejected",
    "skip-justification-rejected",
]
