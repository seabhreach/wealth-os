"""Structured deterministic context for Workspace explanations."""

from __future__ import annotations

from dataclasses import dataclass

from experience.live.models import LiveWorkspace, NarrativeEvidence
from experience.models import GoalId
from experience.workspace_composition.models import WorkspaceComponentType, WorkspaceSpec


@dataclass(frozen=True, slots=True)
class ExplainContext:
    """Evidence-scoped context passed from a Workspace component to Conversation."""

    workspace_id: str
    component_id: str
    component_type: WorkspaceComponentType
    scenario: tuple[tuple[str, str], ...]
    evidence_refs: tuple[str, ...]
    selection: str | None
    allowed_actions: tuple[str, ...] = (
        "ExplainEvidence",
        "HighlightEvidence",
        "ShowDetail",
    )


@dataclass(frozen=True, slots=True)
class DeterministicExplanation:
    """Template explanation and the exact evidence references it used."""

    framing: str
    text: str
    evidence_refs_used: tuple[str, ...]


def context_for_component(
    spec: WorkspaceSpec,
    component_id: str,
    *,
    selection: str | None = None,
) -> ExplainContext:
    """Create structured context from a validated Workspace component."""

    component = spec.component(component_id)
    refs = (
        *component.evidence_refs,
        *(ref for group in component.groups for ref in group.evidence_refs),
    )
    return ExplainContext(
        workspace_id=spec.workspace_id,
        component_id=component.component_id,
        component_type=component.component_type,
        scenario=spec.scenario_overrides,
        evidence_refs=refs,
        selection=selection,
    )


def context_for_evidence(
    workspace: LiveWorkspace,
    component_id: str,
    evidence_refs: tuple[str, ...],
) -> ExplainContext:
    """Create explanation context for a validated goal-specific composition."""

    available = {item.evidence_id for item in workspace.evidence}
    unknown = set(evidence_refs).difference(available)
    if unknown:
        raise ValueError(f"Unknown explanation evidence: {', '.join(sorted(unknown))}")
    return ExplainContext(
        workspace.workspace_id,
        component_id,
        WorkspaceComponentType.METRIC_COMPARISON,
        workspace.provenance.scenario_overrides,
        evidence_refs,
        None,
    )


def explain_context(
    context: ExplainContext,
    workspace: LiveWorkspace,
) -> DeterministicExplanation:
    """Explain only the evidence explicitly referenced by the context."""

    available = {item.evidence_id: item for item in workspace.evidence}
    unknown = set(context.evidence_refs).difference(available)
    if unknown:
        raise ValueError(f"Unknown explanation evidence: {', '.join(sorted(unknown))}")
    scoped = tuple(available[ref] for ref in context.evidence_refs)
    age = dict(context.scenario).get("retirement_age", "the explored age")
    component_name = {
        WorkspaceComponentType.WEALTH_TRAJECTORY: "liquid-assets trajectory",
        WorkspaceComponentType.METRIC_COMPARISON: "baseline comparison",
        WorkspaceComponentType.TIMELINE: "retirement timeline",
    }.get(context.component_type, "Workspace evidence")
    framing = (
        f"You're asking about the {component_name} for retiring at {age}."
        if workspace.goal_id is GoalId.RETIRE_EARLIER
        else f"You're asking about the evidence behind {workspace.title}"
    )

    if context.component_type is WorkspaceComponentType.WEALTH_TRAJECTORY:
        text = (
            "The two paths use the same Financial Picture and planning assumptions. "
            "Only the temporary retirement age changes, so the gap shows how stopping work "
            "earlier changes the liquid assets available to fund spending over time."
        )
    elif (
        context.component_type is WorkspaceComponentType.METRIC_COMPARISON
        and workspace.goal_id is not GoalId.RETIRE_EARLIER
    ):
        narrative = next(
            (item for item in workspace.evidence if isinstance(item, NarrativeEvidence)), None
        )
        text = (
            narrative.text
            if narrative
            else "This explanation is limited to the selected deterministic evidence."
        )
    elif context.component_type is WorkspaceComponentType.METRIC_COMPARISON:
        text = (
            "These figures place the unchanged plan beside the temporary exploration using "
            "the same definitions, periods and deterministic results."
        )
    elif context.component_type is WorkspaceComponentType.TIMELINE:
        text = (
            "The timeline connects the explored retirement date with the existing private- "
            "and State-Pension milestones, making the period funded from other assets visible."
        )
    else:
        narrative = next((item for item in scoped if isinstance(item, NarrativeEvidence)), None)
        text = (
            narrative.text if narrative else "This explanation is limited to the selected evidence."
        )

    return DeterministicExplanation(framing, text, context.evidence_refs)
