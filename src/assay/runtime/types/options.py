"""Engine options (port of ``runtime/types/options.ts``)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from ..enums import AssayAction
from ..id_generator import IdGenerator
from .result import AssayMode


class AssayOptions(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    mode: AssayMode
    # Mandatory IFF mode == "action". Validated at engine entry.
    action: AssayAction | None = None
    id_generator: IdGenerator | None = None
    # When true, justification-rejection states surface as resolvable issues.
    consider_justification_rejection: bool = False
