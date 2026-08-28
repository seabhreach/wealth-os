"""Typed serializable contracts for the bounded G-001 Workspace prototype."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

from experience.models import GoalId

WORKSPACE_SPEC_VERSION = "workspace-spec/v1"


class WorkspaceComponentType(StrEnum):
    """RFC-013 component types used by the G-001 prototype."""

    ANSWER = "ANSWER"
    WEALTH_TRAJECTORY = "WEALTH_TRAJECTORY"
    TIMELINE = "TIMELINE"
    METRIC_COMPARISON = "METRIC_COMPARISON"
    TRADE_OFF = "TRADE_OFF"
    NARRATIVE = "NARRATIVE"
    ASSUMPTION = "ASSUMPTION"
    LIMITATION = "LIMITATION"
    DISCLOSURE = "DISCLOSURE"


class DisclosureContent(StrEnum):
    """Bounded secondary content that the prototype renderer understands."""

    EVIDENCE = "evidence"
    PROVENANCE = "provenance"


@dataclass(frozen=True, slots=True)
class ComponentGroupSpec:
    """Semantic grouping of evidence within one component."""

    label: str
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WorkspaceComponentSpec:
    """One visual component containing references rather than financial values."""

    component_id: str
    component_type: WorkspaceComponentType
    title: str
    evidence_refs: tuple[str, ...] = ()
    groups: tuple[ComponentGroupSpec, ...] = ()
    disclosure_content: DisclosureContent | None = None
    accessibility_label: str | None = None


@dataclass(frozen=True, slots=True)
class WorkspaceSectionSpec:
    """Ordered semantic section independent of pixel layout."""

    section_id: str
    components: tuple[WorkspaceComponentSpec, ...]
    secondary: bool = False


@dataclass(frozen=True, slots=True)
class ScenarioControlSpec:
    """One bounded control mapped to a registered temporary override."""

    control_id: str
    label: str
    control_type: str
    allowed_values: tuple[int, ...]
    baseline_value: int
    current_value: int
    override_mapping_id: str
    affected_evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SetScenarioValue:
    """Validated action shared by visual and future conversational controls."""

    control_id: str
    value: int


@dataclass(frozen=True, slots=True)
class WorkspaceSpecProvenance:
    """Composition identity kept separate from financial-result identity."""

    baseline_identifier: str
    financial_picture_fingerprint: str
    result_fingerprint: str
    composition_policy_version: str
    workspace_spec_version: str = WORKSPACE_SPEC_VERSION


@dataclass(frozen=True, slots=True)
class WorkspaceSpec:
    """Validated renderer contract for one question-specific Workspace."""

    spec_version: str
    workspace_id: str
    goal_id: GoalId
    question: str
    answer_component_id: str
    scenario_overrides: tuple[tuple[str, str], ...]
    sections: tuple[WorkspaceSectionSpec, ...]
    controls: tuple[ScenarioControlSpec, ...]
    assumption_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    provenance: WorkspaceSpecProvenance

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-ready representation without renderer state."""

        return asdict(self)

    @property
    def components(self) -> tuple[WorkspaceComponentSpec, ...]:
        """Return components in semantic render order."""

        return tuple(component for section in self.sections for component in section.components)

    def component(self, component_id: str) -> WorkspaceComponentSpec:
        """Resolve one component by stable identifier."""

        try:
            return next(item for item in self.components if item.component_id == component_id)
        except StopIteration as error:
            raise KeyError(component_id) from error


class WorkspaceSpecValidationError(ValueError):
    """Raised when a proposed Workspace violates the bounded composition policy."""
