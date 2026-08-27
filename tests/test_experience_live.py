"""Focused contracts for the read-only deterministic Experience integration."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from experience.live.models import (
    ComparisonEvidence,
    EvidenceMode,
    FinancialStatementEvidence,
    LimitationEvidence,
    NarrativeEvidence,
)
from experience.live.provenance import provenance_identity, stable_fingerprint
from experience.live.service import LiveExperienceService
from experience.models import EvidencePurpose, GoalId
from streamlit.testing.v1 import AppTest

from engine.reporting import (
    AdvisorScenario,
    ScenarioOverride,
    annual_financial_statement,
    run_scenario,
)

ROOT = Path(__file__).resolve().parents[1]
LIVE_ROOT = ROOT / "experience" / "live"
LIVE_RENDERER = ROOT / "experience" / "components" / "live_workspace.py"


def test_live_modules_use_only_approved_engine_boundaries() -> None:
    engine_imports: set[str] = set()
    for path in LIVE_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module.startswith("engine")
            ):
                engine_imports.add(node.module)
            elif isinstance(node, ast.Import):
                engine_imports.update(
                    alias.name for alias in node.names if alias.name.startswith("engine")
                )

    assert engine_imports
    assert all(
        module == "engine.config" or module.startswith("engine.reporting")
        for module in engine_imports
    )
    assert all(
        "dashboard" not in path.read_text(encoding="utf-8") for path in LIVE_ROOT.rglob("*.py")
    )


def test_live_renderer_has_no_engine_imports_or_financial_arithmetic() -> None:
    source = LIVE_RENDERER.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(LIVE_RENDERER))
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


def test_evidence_models_are_immutable_and_answer_first() -> None:
    workspace = _service().retire_earlier(58)

    assert isinstance(workspace.evidence[0], NarrativeEvidence)
    assert workspace.evidence[0].purpose is EvidencePurpose.ANSWER
    with pytest.raises(FrozenInstanceError):
        workspace.evidence[0].title = "Changed"  # type: ignore[misc]


def test_mock_and_live_evidence_cannot_mix() -> None:
    workspace = _service().retire_earlier(58)
    mock_item = replace(workspace.evidence[0], mode=EvidenceMode.MOCK)

    with pytest.raises(ValueError, match="cannot be mixed"):
        replace(workspace, evidence=(mock_item, *workspace.evidence[1:]))


def test_baseline_configuration_remains_identical_after_every_supported_scenario() -> None:
    service = _service()
    config = service.baseline.configuration
    before = config.model_dump_json()

    service.retire_earlier(58)
    service.property_decision()
    service.employer_equity()
    service.higher_spending(Decimal("100000"))
    service.cash_decline(2032)

    assert config.model_dump_json() == before
    assert config.household.planned_retirement_age == 60
    assert config.amazon_rsus.sell_on_vest is True
    assert config.assumptions.target_retirement_income == Decimal("80000")
    assert len(config.rental_properties) == 1


def test_retirement_age_workspace_matches_existing_scenario_result() -> None:
    service = _service()
    workspace = service.retire_earlier(58)
    existing = run_scenario(
        service.baseline.configuration,
        AdvisorScenario("Existing API check", ScenarioOverride(retirement_age=58)),
    )
    comparison = _comparison(workspace.evidence, "g001-net-worth")

    assert workspace.goal_id is GoalId.RETIRE_EARLIER
    assert comparison.scenario_value == existing.metrics.final_net_worth
    assert existing.metrics.retirement_age == 58
    assert service.baseline.configuration.household.planned_retirement_age == 60
    assert workspace.proposed_update is not None


def test_live_adapter_rejects_out_of_boundary_temporary_inputs() -> None:
    service = _service()

    with pytest.raises(ValueError, match="projection horizon"):
        service.retire_earlier(53)
    with pytest.raises(ValueError, match="must not be negative"):
        service.higher_spending(Decimal("-1"))


def test_retirement_evidence_uses_projection_values_without_recalculation() -> None:
    service = _service()
    workspace = service.retire_earlier(58)
    existing = run_scenario(
        service.baseline.configuration,
        AdvisorScenario("Existing API check", ScenarioOverride(retirement_age=58)),
    )
    timeline = next(
        item for item in workspace.evidence if item.evidence_id == "g001-liquid-timeline"
    )

    assert timeline.points[0].value == existing.projection[0].liquid_assets  # type: ignore[union-attr]
    assert timeline.points[-1].value == existing.projection[-1].liquid_assets  # type: ignore[union-attr]


def test_property_workspace_compares_configured_include_and_exclude_results() -> None:
    service = _service()
    workspace = service.property_decision()
    excluded = run_scenario(
        service.baseline.configuration,
        AdvisorScenario(
            "Existing API check",
            ScenarioOverride(include_planned_rental_properties=False),
        ),
    )
    comparison = _comparison(workspace.evidence, "g002-property-value")

    assert comparison.scenario_value == excluded.metrics.final_property_value
    assert excluded.metrics.final_property_value == Decimal("0")
    assert service.baseline.configuration.rental_properties


def test_property_financing_returns_only_an_explicit_unsupported_result() -> None:
    workspace = _service().property_decision(financing=True)

    assert isinstance(workspace.evidence[0], NarrativeEvidence)
    assert any(isinstance(item, LimitationEvidence) for item in workspace.evidence)
    assert not any(isinstance(item, ComparisonEvidence) for item in workspace.evidence)
    assert "Mortgage" in repr(workspace.evidence)


def test_employer_equity_uses_supported_disposal_policy_metrics() -> None:
    service = _service()
    workspace = service.employer_equity()
    sell = run_scenario(
        service.baseline.configuration,
        AdvisorScenario("Sell", ScenarioOverride(sell_on_vest=True)),
    )
    retain = run_scenario(
        service.baseline.configuration,
        AdvisorScenario("Retain", ScenarioOverride(sell_on_vest=False)),
    )
    concentration = _comparison(workspace.evidence, "g003-concentration")

    assert concentration.baseline_value == sell.metrics.maximum_amazon_concentration
    assert concentration.scenario_value == retain.metrics.maximum_amazon_concentration
    assert isinstance(concentration.baseline_value, Decimal)
    assert isinstance(concentration.scenario_value, Decimal)
    assert concentration.scenario_value > concentration.baseline_value


def test_experience_does_not_define_a_concentration_formula() -> None:
    source = (LIVE_ROOT / "service.py").read_text(encoding="utf-8")
    tree = ast.parse(source, filename="service.py")
    method = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "employer_equity"
    )

    assert "maximum_amazon_concentration" in source
    assert not any(
        isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div) for node in ast.walk(method)
    )


def test_permanent_spending_uses_existing_supported_override() -> None:
    service = _service()
    target = Decimal("100000")
    workspace = service.higher_spending(target)
    existing = run_scenario(
        service.baseline.configuration,
        AdvisorScenario(
            "Existing API check",
            ScenarioOverride(target_retirement_spending=target),
        ),
    )
    comparison = _comparison(workspace.evidence, "g004-spending")

    assert comparison.scenario_value == existing.metrics.first_retirement_spending
    assert service.baseline.configuration.assumptions.target_retirement_income == Decimal("80000")


def test_temporary_multi_year_spending_is_an_explicit_limitation() -> None:
    workspace = _service().higher_spending(Decimal("100000"), temporary_years=5)

    assert any(isinstance(item, LimitationEvidence) for item in workspace.evidence)
    assert not any(isinstance(item, ComparisonEvidence) for item in workspace.evidence)
    assert "no supported override" in repr(workspace.evidence).casefold()


def test_cash_decline_uses_existing_statement_and_trace_for_selected_year() -> None:
    service = _service()
    workspace = service.cash_decline(2032)
    expected = annual_financial_statement(
        run_scenario(
            service.baseline.configuration,
            AdvisorScenario("Baseline", ScenarioOverride()),
        ).projection,
        service.baseline.configuration,
        2032,
    )
    statement = next(
        item for item in workspace.evidence if isinstance(item, FinancialStatementEvidence)
    )

    assert statement.opening_cash == expected.assets.trace.opening_cash
    assert statement.closing_cash == expected.assets.trace.closing_cash
    assert statement.liquid_assets == expected.liquid_assets
    assert statement.net_worth == expected.net_worth


def test_cash_decline_is_causal_and_requires_no_data_collection() -> None:
    workspace = _service().cash_decline(2032)
    answer = workspace.evidence[0]

    assert isinstance(answer, NarrativeEvidence)
    assert "opening cash" in answer.text.casefold()
    assert "closing cash" in answer.text.casefold()
    assert "question" not in repr(workspace).casefold()
    assert workspace.proposed_update is None


def test_fingerprints_are_stable_and_timestamp_is_not_identity() -> None:
    service = _service()
    first = service.retire_earlier(58).provenance
    second = service.retire_earlier(58).provenance
    later = replace(first, generated_at=first.generated_at + timedelta(days=1))

    assert first.financial_picture_fingerprint == second.financial_picture_fingerprint
    assert first.result_fingerprint == second.result_fingerprint
    assert provenance_identity(first) == provenance_identity(second)
    assert provenance_identity(first) == provenance_identity(later)
    assert stable_fingerprint(service.baseline.configuration) == first.financial_picture_fingerprint


def test_material_override_changes_result_identity() -> None:
    service = _service()

    assert (
        service.retire_earlier(58).provenance.result_fingerprint
        != service.retire_earlier(59).provenance.result_fingerprint
    )


def test_live_and_mock_modes_are_visibly_separate_in_streamlit() -> None:
    app = AppTest.from_file(str(ROOT / "experience" / "app.py")).run(timeout=30)
    app.radio(key="wealth_os_experience_mode").set_value("LIVE DETERMINISTIC EXPERIENCE").run(
        timeout=30
    )

    assert not app.exception
    rendered = "\n".join(markdown.value for markdown in app.markdown)
    assert "Choose a question to explore with the v0.2 baseline." in rendered
    assert "No mock evidence" in rendered

    app.button(key="live-goal-G-005").click().run(timeout=30)
    assert not app.exception
    rendered = "\n".join(markdown.value for markdown in app.markdown)
    assert "Live deterministic Workspace" in rendered
    assert "Cash Decline Explanation" in rendered
    assert "Illustrative mock Workspace" not in rendered


def _service() -> LiveExperienceService:
    return LiveExperienceService.from_example(ROOT)


def _comparison(evidence: tuple[object, ...], evidence_id: str) -> ComparisonEvidence:
    item = next(
        candidate
        for candidate in evidence
        if isinstance(candidate, ComparisonEvidence) and candidate.evidence_id == evidence_id
    )
    return item
