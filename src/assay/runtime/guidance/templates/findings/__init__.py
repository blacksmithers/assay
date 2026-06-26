"""Finding-template dispatchers (port of ``templates/findings/index.ts``)."""

from __future__ import annotations

from ....types.finding import AssayCheckType
from .acceptance_coverage import acceptance_coverage_dispatcher
from .file_action_coverage import file_action_coverage_dispatcher
from .implementation_coverage import implementation_coverage_dispatcher
from .template_types import FindingTemplate, FindingTemplateDispatcher
from .test_result_presence import test_result_presence_dispatcher

finding_templates: dict[AssayCheckType, FindingTemplateDispatcher] = {
    "acceptance-coverage": acceptance_coverage_dispatcher,
    "implementation-coverage": implementation_coverage_dispatcher,
    "file-action-coverage": file_action_coverage_dispatcher,
    "test-result-presence": test_result_presence_dispatcher,
}

__all__ = [
    "FindingTemplate",
    "FindingTemplateDispatcher",
    "acceptance_coverage_dispatcher",
    "file_action_coverage_dispatcher",
    "finding_templates",
    "implementation_coverage_dispatcher",
    "test_result_presence_dispatcher",
]
