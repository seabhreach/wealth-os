"""Deterministic G-001 composition policy over immutable live evidence."""

from __future__ import annotations

from experience.live.models import LiveWorkspace
from experience.models import GoalId
from experience.workspace_composition.models import (
    WORKSPACE_SPEC_VERSION,
    ComponentGroupSpec,
    DisclosureContent,
    ScenarioControlSpec,
    WorkspaceComponentSpec,
    WorkspaceComponentType,
    WorkspaceSectionSpec,
    WorkspaceSpec,
    WorkspaceSpecProvenance,
    WorkspaceSpecValidationError,
)

G001_COMPOSITION_POLICY_VERSION = "g001-visual-workspace/v1"
G001_REQUIRED_SECTION_ORDER = (
    "answer",
    "primary",
    "timeline",
    "trade-off",
    "explanation",
    "details",
)
G001_REQUIRED_COMPONENT_ORDER = (
    WorkspaceComponentType.ANSWER,
    WorkspaceComponentType.WEALTH_TRAJECTORY,
    WorkspaceComponentType.METRIC_COMPARISON,
    WorkspaceComponentType.TIMELINE,
    WorkspaceComponentType.TRADE_OFF,
    WorkspaceComponentType.NARRATIVE,
    WorkspaceComponentType.ASSUMPTION,
    WorkspaceComponentType.DISCLOSURE,
    WorkspaceComponentType.LIMITATION,
    WorkspaceComponentType.DISCLOSURE,
)


def compose_g001_workspace(
    workspace: LiveWorkspace,
    *,
    allowed_retirement_ages: tuple[int, ...],
    baseline_retirement_age: int,
    explored_retirement_age: int,
) -> WorkspaceSpec:
    """Compose the fixed G-001 visual grammar using evidence references only."""

    available = {item.evidence_id for item in workspace.evidence}
    milestone_refs = tuple(
        evidence_id
        for evidence_id in (
            "g001-milestone-explored-retirement",
            "g001-milestone-baseline-retirement",
            "g001-milestone-private-pension",
            "g001-milestone-state-pension",
        )
        if evidence_id in available
    )
    explanation_refs = tuple(
        evidence_id
        for evidence_id in (
            "g001-liquid-scenario-series",
            "g001-milestone-explored-retirement",
            "g001-milestone-private-pension",
            "g001-milestone-state-pension",
        )
        if evidence_id in available
    )
    spec = WorkspaceSpec(
        spec_version=WORKSPACE_SPEC_VERSION,
        workspace_id=workspace.workspace_id,
        goal_id=GoalId.RETIRE_EARLIER,
        question=f"Could I retire at {explored_retirement_age}?",
        answer_component_id="g001-answer-component",
        scenario_overrides=workspace.provenance.scenario_overrides,
        sections=(
            WorkspaceSectionSpec(
                "answer",
                (
                    WorkspaceComponentSpec(
                        "g001-answer-component",
                        WorkspaceComponentType.ANSWER,
                        "Answer",
                        ("g001-answer",),
                    ),
                ),
            ),
            WorkspaceSectionSpec(
                "primary",
                (
                    WorkspaceComponentSpec(
                        "g001-trajectory-component",
                        WorkspaceComponentType.WEALTH_TRAJECTORY,
                        "Liquid assets over time",
                        (
                            "g001-liquid-baseline-series",
                            "g001-liquid-scenario-series",
                            *tuple(
                                ref
                                for ref in milestone_refs
                                if ref != "g001-milestone-baseline-retirement"
                            ),
                        ),
                        accessibility_label=(
                            "Annual liquid-assets trajectories for the baseline and explored "
                            "retirement ages."
                        ),
                    ),
                    WorkspaceComponentSpec(
                        "g001-comparison-component",
                        WorkspaceComponentType.METRIC_COMPARISON,
                        "At a glance",
                        (
                            "g001-age",
                            "g001-funding-status",
                            "g001-liquid-final",
                            "g001-net-worth",
                        ),
                    ),
                ),
            ),
            WorkspaceSectionSpec(
                "timeline",
                (
                    WorkspaceComponentSpec(
                        "g001-timeline-component",
                        WorkspaceComponentType.TIMELINE,
                        "The retirement bridge",
                        milestone_refs,
                        accessibility_label=(
                            "Retirement and income-source milestones in date order."
                        ),
                    ),
                ),
            ),
            WorkspaceSectionSpec(
                "trade-off",
                (
                    WorkspaceComponentSpec(
                        "g001-trade-off-component",
                        WorkspaceComponentType.TRADE_OFF,
                        "The trade-off",
                        groups=(
                            ComponentGroupSpec("Time", ("g001-tradeoff-time",)),
                            ComponentGroupSpec("Financial effect", ("g001-tradeoff-financial",)),
                            ComponentGroupSpec("Held constant", ("g001-tradeoff-constant",)),
                        ),
                    ),
                ),
            ),
            WorkspaceSectionSpec(
                "explanation",
                (
                    WorkspaceComponentSpec(
                        "g001-explanation-component",
                        WorkspaceComponentType.NARRATIVE,
                        "Why?",
                        ("g001-explanation", *explanation_refs),
                    ),
                ),
            ),
            WorkspaceSectionSpec(
                "details",
                (
                    WorkspaceComponentSpec(
                        "g001-assumptions-component",
                        WorkspaceComponentType.ASSUMPTION,
                        "Show assumptions",
                        ("g001-assumption", "g001-spending-assumption"),
                        disclosure_content=DisclosureContent.EVIDENCE,
                    ),
                    WorkspaceComponentSpec(
                        "g001-supporting-component",
                        WorkspaceComponentType.DISCLOSURE,
                        "Show supporting figures",
                        ("g001-bridge",),
                        disclosure_content=DisclosureContent.EVIDENCE,
                    ),
                    WorkspaceComponentSpec(
                        "g001-limitations-component",
                        WorkspaceComponentType.LIMITATION,
                        "Show limitations",
                        ("g001-limitation",),
                        disclosure_content=DisclosureContent.EVIDENCE,
                    ),
                    WorkspaceComponentSpec(
                        "g001-provenance-component",
                        WorkspaceComponentType.DISCLOSURE,
                        "Show provenance",
                        disclosure_content=DisclosureContent.PROVENANCE,
                    ),
                ),
                secondary=True,
            ),
        ),
        controls=(
            ScenarioControlSpec(
                control_id="retirement_age",
                label="Explore retirement age",
                control_type="discrete_choice",
                allowed_values=allowed_retirement_ages,
                baseline_value=baseline_retirement_age,
                current_value=explored_retirement_age,
                override_mapping_id="scenario.retirement_age",
                affected_evidence=tuple(sorted(available)),
            ),
        ),
        assumption_refs=("g001-assumption", "g001-spending-assumption"),
        limitation_refs=("g001-limitation",),
        provenance=WorkspaceSpecProvenance(
            baseline_identifier=workspace.provenance.baseline_identifier,
            financial_picture_fingerprint=(workspace.provenance.financial_picture_fingerprint),
            result_fingerprint=workspace.provenance.result_fingerprint,
            composition_policy_version=G001_COMPOSITION_POLICY_VERSION,
        ),
    )
    validate_g001_workspace(spec, available)
    return spec


def validate_g001_workspace(spec: WorkspaceSpec, available_evidence_ids: set[str]) -> None:
    """Reject references, components, controls, or ordering outside the G-001 policy."""

    if spec.goal_id is not GoalId.RETIRE_EARLIER:
        raise WorkspaceSpecValidationError("G-001 policy requires the retire-earlier goal.")
    if tuple(section.section_id for section in spec.sections) != G001_REQUIRED_SECTION_ORDER:
        raise WorkspaceSpecValidationError("G-001 section ordering is invalid.")
    if tuple(item.component_type for item in spec.components) != G001_REQUIRED_COMPONENT_ORDER:
        raise WorkspaceSpecValidationError("G-001 required components or ordering are invalid.")
    if spec.components[0].component_id != spec.answer_component_id:
        raise WorkspaceSpecValidationError("The direct answer must be the first component.")
    referenced = {
        evidence_id
        for component in spec.components
        for evidence_id in (
            *component.evidence_refs,
            *(ref for group in component.groups for ref in group.evidence_refs),
        )
    }
    referenced.update(spec.assumption_refs)
    referenced.update(spec.limitation_refs)
    unknown = referenced.difference(available_evidence_ids)
    if unknown:
        raise WorkspaceSpecValidationError(
            f"Unknown evidence references: {', '.join(sorted(unknown))}"
        )
    if len(spec.controls) != 1 or spec.controls[0].control_id != "retirement_age":
        raise WorkspaceSpecValidationError("G-001 requires one retirement-age control.")
    control = spec.controls[0]
    if control.current_value not in control.allowed_values:
        raise WorkspaceSpecValidationError("Current retirement age is outside the allowed set.")
    if control.baseline_value not in control.allowed_values:
        raise WorkspaceSpecValidationError("Baseline retirement age is outside the allowed set.")
    if control.override_mapping_id != "scenario.retirement_age":
        raise WorkspaceSpecValidationError("Retirement control has an unknown override mapping.")
