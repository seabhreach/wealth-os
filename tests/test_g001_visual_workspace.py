"""Contracts for the visual-first G-001 Workspace prototype."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest
from experience.display import format_compact_currency
from experience.live.models import TimelineEvidence
from experience.live.scenario_actions import g001_scenario_override
from experience.live.service import LiveExperienceService
from experience.workspace_composition import (
    SetScenarioValue,
    WorkspaceComponentType,
    WorkspaceSpec,
    compose_g001_workspace,
    validate_g001_workspace,
)
from experience.workspace_composition.models import WorkspaceSpecValidationError
from streamlit.testing.v1 import AppTest

from engine.reporting import ScenarioOverride

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "experience" / "components" / "g001_visual_workspace.py"


def test_g001_spec_is_serializable_answer_first_and_uses_known_evidence() -> None:
    service = _service()
    workspace = service.retire_earlier(58)
    spec = _spec(service, 58)
    evidence_ids = {item.evidence_id for item in workspace.evidence}

    assert spec.components[0].component_type is WorkspaceComponentType.ANSWER
    assert spec.sections[-1].secondary
    assert spec.to_dict()["question"] == "Could I retire at 58?"
    validate_g001_workspace(spec, evidence_ids)
    with pytest.raises(FrozenInstanceError):
        spec.question = "Changed"  # type: ignore[misc]


def test_g001_spec_rejects_unknown_evidence_and_changed_order() -> None:
    service = _service()
    workspace = service.retire_earlier(58)
    spec = _spec(service, 58)
    evidence_ids = {item.evidence_id for item in workspace.evidence}
    trajectory = spec.sections[1].components[0]
    unknown = replace(trajectory, evidence_refs=(*trajectory.evidence_refs, "unknown"))
    unknown_section = replace(
        spec.sections[1], components=(unknown, *spec.sections[1].components[1:])
    )

    with pytest.raises(WorkspaceSpecValidationError, match="Unknown evidence"):
        validate_g001_workspace(
            replace(spec, sections=(spec.sections[0], unknown_section, *spec.sections[2:])),
            evidence_ids,
        )
    with pytest.raises(WorkspaceSpecValidationError, match="ordering"):
        validate_g001_workspace(
            replace(spec, sections=tuple(reversed(spec.sections))), evidence_ids
        )


def test_retirement_control_maps_only_to_existing_scenario_override() -> None:
    service = _service()
    action = SetScenarioValue("retirement_age", 58)

    assert g001_scenario_override(service.baseline.configuration, action) == ScenarioOverride(
        retirement_age=58
    )
    with pytest.raises(ValueError, match="only the retirement-age"):
        g001_scenario_override(
            service.baseline.configuration,
            SetScenarioValue("spending", 58),
        )
    with pytest.raises(ValueError, match="G-001 range"):
        g001_scenario_override(
            service.baseline.configuration,
            SetScenarioValue("retirement_age", 56),
        )


def test_age_changes_result_identity_but_never_mutates_baseline() -> None:
    service = _service()
    baseline = service.baseline.configuration
    baseline_age = baseline.household.planned_retirement_age

    at_58 = service.retire_earlier(58)
    at_59 = service.retire_earlier(59)

    assert at_58.provenance.result_fingerprint != at_59.provenance.result_fingerprint
    assert (
        at_58.provenance.result_fingerprint
        == service.retire_earlier(58).provenance.result_fingerprint
    )
    assert service.baseline.configuration is baseline
    assert service.baseline.configuration.household.planned_retirement_age == baseline_age


def test_visual_trajectory_contains_full_exact_engine_evidence() -> None:
    workspace = _service().retire_earlier(58)
    series = [item for item in workspace.evidence if isinstance(item, TimelineEvidence)]
    baseline = next(item for item in series if item.evidence_id == "g001-liquid-baseline-series")
    scenario = next(item for item in series if item.evidence_id == "g001-liquid-scenario-series")

    assert len(baseline.points) == len(scenario.points)
    assert len(scenario.points) > 20
    assert all(point.age is not None for point in scenario.points)
    exact = scenario.points[-1].value
    assert scenario.points[-1].value == exact


def test_compact_formatting_does_not_expose_decimal_tails() -> None:
    workspace = _service().retire_earlier(58)
    scenario = next(
        item
        for item in workspace.evidence
        if isinstance(item, TimelineEvidence) and item.evidence_id == "g001-liquid-scenario-series"
    )
    exact = scenario.points[-1].value
    rendered = format_compact_currency(exact)

    assert rendered.startswith("€")
    assert len(rendered) < 12
    assert scenario.points[-1].value == exact


def test_visual_renderer_has_no_engine_imports_or_financial_arithmetic() -> None:
    source = RENDERER.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(RENDERER))
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    financial_operators = (ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Pow)

    assert not any(module.startswith("engine") for module in imports)
    assert not any(
        isinstance(node, ast.BinOp) and isinstance(node.op, financial_operators)
        for node in ast.walk(tree)
    )


def test_g001_visual_workspace_renders_and_age_control_updates_in_place() -> None:
    app = AppTest.from_file(str(ROOT / "experience" / "app.py")).run(timeout=30)
    app.chat_input(key="home-chat-input").set_value("Can I retire at 59?").run(timeout=30)
    app.button(key="conversation-open-workspace").click().run(timeout=30)

    assert not app.exception
    assert app.selectbox(key="g001-retirement-age").value == 59
    rendered = "\n".join(markdown.value for markdown in app.markdown)
    assert "Could I retire at 59?" in rendered
    assert "Baseline retirement age" in rendered
    assert "Liquid assets over time" in rendered
    assert "The retirement bridge" in rendered
    assert "Why?" in rendered
    assert "Recommended" not in rendered
    assert "Optimal" not in rendered
    assert "ScenarioOverride" not in rendered
    assert {item.label for item in app.expander} == {"About this projection"}
    assert "Show provenance" not in rendered

    app.selectbox(key="g001-retirement-age").set_value(57).run(timeout=30)
    assert not app.exception
    rendered = "\n".join(markdown.value for markdown in app.markdown)
    assert "Could I retire at 57?" in rendered
    assert "Exploring <strong>57</strong>" in rendered


def _service() -> LiveExperienceService:
    return LiveExperienceService.from_example(ROOT)


def _spec(service: LiveExperienceService, age: int) -> WorkspaceSpec:
    workspace = service.retire_earlier(age)
    return compose_g001_workspace(
        workspace,
        allowed_retirement_ages=service.supported_retirement_ages,
        baseline_retirement_age=(service.baseline.configuration.household.planned_retirement_age),
        explored_retirement_age=age,
    )
