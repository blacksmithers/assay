"""Work-session / spec input contracts + :class:`AssayContext`.

These mirror the zod-inferred ``WorkSession*`` shapes (``@specforge/session-types``)
and the ``Ticket`` shape (``@specforge/spec-types``) consumed by the engine.
They subclass :class:`InputModel`: unknown keys are ignored (zod strips them),
defaults match the zod ``.default(...)`` calls, and :meth:`to_input_dict`
reproduces the zod-parsed JSON shape for objects the engine embeds in its output.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from ._base import InputModel
from .config import AssayforgeConfig

# ---- spec-types (auxiliary) ----

ExpectedAction = Literal["create", "modify", "delete", "reference"]
ActualAction = Literal["created", "modified", "deleted", "referenced", "absent"]
FileChangeStatus = Literal["matched", "missing", "mismatched", "extra"]
JustificationApproved = Literal["pending", "approved", "rejected"]
WorkSessionStatus = Literal["active", "completed", "closed"]
TestType = Literal[
    "unit", "integration", "e2e", "typecheck", "lint", "build",
    "contract", "structural", "layout", "a11y", "performance",
]
TicketType = Literal["implementation", "verification"]
Complexity = Literal["small", "medium", "large", "xlarge"]


class FieldDeclaration(InputModel):
    value: Literal["N/A"]
    reason: str


class AcceptanceCriterion(InputModel):
    id: str
    given: str
    when: str
    then: str
    order: int


class ImplementationStep(InputModel):
    id: str
    text: str
    order: int


class TestSpecification(InputModel):
    test_types: list[TestType]
    quality_gates: list[str]
    test_commands: list[str]
    coverage_target: float | None = None


class Ticket(InputModel):
    id: str
    epic_id: str
    ticket_number: int | None = None
    title: str
    description: str | None = None
    ticket_type: TicketType
    complexity: Complexity
    estimated_minutes: int
    order: int | None = None
    acceptance_criteria: list[AcceptanceCriterion] = Field(default_factory=list)
    implementation_steps: list[ImplementationStep] = Field(default_factory=list)
    files_to_be_created: list[str] = Field(default_factory=list)
    files_to_be_modified: list[str] = Field(default_factory=list)
    files_to_be_deleted: list[str] = Field(default_factory=list)
    files_to_be_referenced: list[str] = Field(default_factory=list)
    test_specification: TestSpecification | None = None
    guardrails: list[str] = Field(default_factory=list)
    code_references: list[Any] = Field(default_factory=list)
    type_references: list[Any] = Field(default_factory=list)
    code_snippets: list[Any] | None = None
    type_snippets: list[Any] | None = None
    blueprint_references: list[Any] = Field(default_factory=list)
    dependencies: list[Any] = Field(default_factory=list)
    field_declarations: dict[str, FieldDeclaration] | None = None


# ---- session-types ----


class WorkSession(InputModel):
    id: str
    ticket_id: str
    project_id: str
    status: WorkSessionStatus
    started_at: str
    completed_at: str | None = None
    closed_at: str | None = None


class WorkSessionAcceptanceCheck(InputModel):
    id: str
    work_session_id: str
    criterion_id: str
    ticket_id: str
    project_id: str
    checked: bool
    checked_at: str | None = None


class WorkSessionImplStepCompletion(InputModel):
    id: str
    work_session_id: str
    step_id: str
    ticket_id: str
    project_id: str
    done: bool
    done_at: str | None = None


class WorkSessionFileChange(InputModel):
    id: str
    work_session_id: str
    ticket_id: str
    project_id: str
    expected_path: str
    expected_action: ExpectedAction
    actual_action: ActualAction | None = None
    status: FileChangeStatus
    justification: str | None = None
    justification_approved: JustificationApproved = "pending"
    notes: str | None = None
    line_count: int | None = None
    commit_hash: str | None = None
    recorded_at: str


class WorkSessionTestResult(InputModel):
    id: str
    work_session_id: str
    project_id: str
    test_type: TestType
    passed: int
    failed: int
    skipped: int = 0
    total: int
    all_passed: bool
    output: str | None = None
    command: str | None = None
    exit_code: int | None = None
    duration_ms: int | None = None
    error_count: int | None = None
    warning_count: int | None = None
    summary: str | None = None
    suites: Any | None = None
    skipped_justifications: list[str] = Field(default_factory=list)
    failure_justifications: list[str] = Field(default_factory=list)
    notes: str | None = None
    run_at: str


class AssayContext(InputModel):
    ticket: Ticket
    work_session: WorkSession
    acceptance_checks: list[WorkSessionAcceptanceCheck] = Field(default_factory=list)
    impl_step_completions: list[WorkSessionImplStepCompletion] = Field(default_factory=list)
    file_changes: list[WorkSessionFileChange] = Field(default_factory=list)
    test_results: list[WorkSessionTestResult] = Field(default_factory=list)
    config: AssayforgeConfig | None = None
