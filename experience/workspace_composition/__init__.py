"""Bounded Workspace composition contracts for visual prototypes."""

from experience.workspace_composition.g001 import (
    G001_COMPOSITION_POLICY_VERSION,
    compose_g001_workspace,
    validate_g001_workspace,
)
from experience.workspace_composition.models import (
    ComponentGroupSpec,
    DisclosureContent,
    ScenarioControlSpec,
    SetScenarioValue,
    WorkspaceComponentSpec,
    WorkspaceComponentType,
    WorkspaceSectionSpec,
    WorkspaceSpec,
)

__all__ = [
    "G001_COMPOSITION_POLICY_VERSION",
    "ComponentGroupSpec",
    "DisclosureContent",
    "ScenarioControlSpec",
    "SetScenarioValue",
    "WorkspaceComponentSpec",
    "WorkspaceComponentType",
    "WorkspaceSectionSpec",
    "WorkspaceSpec",
    "compose_g001_workspace",
    "validate_g001_workspace",
]
