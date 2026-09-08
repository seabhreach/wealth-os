"""Focused contracts for the read-only deterministic Experience integration."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from experience.components.live_workspace import _evidence_groups
from experience.display import format_display_value, format_table_value
from experience.live.models import (
    AssumptionEvidence,
    ComparisonEvidence,
    EvidenceMode,
    FinancialStatementEvidence,
    LimitationEvidence,
    MetricEvidence,
    NarrativeEvidence,
    TableEvidence,
    TimelineEvidence,
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


def test_financial_picture_exposes_inactive_primary_residence_separately() -> None:
    """The home is visible household data, not an available planning asset."""
    picture = _service().baseline.financial_picture
    items = {item.key: item.value for item in picture.items}

    assert items["primary_residence:value"] == Decimal("1500000")
    assert items["primary_residence:mortgage"] == Decimal("0")
    assert items["primary_residence:equity"] == Decimal("1500000")
    assert "not assumed available" in str(items["primary_residence:planning_status"])


def test_financial_picture_exposes_canonical_investment_holding_details() -> None:
    """Ordinary investments are visible by identity, type, and current value."""
    picture = _service().baseline.financial_picture
    items = {item.key: item.value for item in picture.items}

    assert items["investments"] == Decimal("300000")
    assert items["investment:existing-etf:name"] == "Existing ETF holding"
    assert items["investment:existing-etf:type"] == "ETF"
    assert items["investment:existing-etf:value"] == Decimal("300000")


def test_financial_picture_keeps_household_planning_and_liquid_totals_distinct() -> None:
    """Presentation summaries retain the primary-residence and access boundaries."""
    items = {item.key: item.value for item in _service().baseline.financial_picture.items}

    assert items["employer_equity:value"] == Decimal("77004.00")
    assert items["summary:liquid_investable_assets"] == Decimal("877004.00")
    assert items["summary:retirement_assets"] == Decimal("700000")
    assert items["summary:planning_net_worth"] == Decimal("1577004.00")
    assert items["summary:household_net_worth"] == Decimal("3077004.00")
    household_net_worth = items["summary:household_net_worth"]
    planning_net_worth = items["summary:planning_net_worth"]
    residence_equity = items["primary_residence:equity"]
    assert isinstance(household_net_worth, Decimal)
    assert isinstance(planning_net_worth, Decimal)
    assert isinstance(residence_equity, Decimal)
    assert household_net_worth - planning_net_worth == residence_equity


def test_financial_picture_marks_planned_property_and_pension_access_context() -> None:
    items = {item.key: item.value for item in _service().baseline.financial_picture.items}

    assert items["property:Ardfield Court:status"] == "Planned purchase"
    assert items["property:Ardfield Court:value"] == Decimal("0")
    assert items["property:Ardfield Court:rent_growth"] == Decimal("0.02")
    assert items["pension:Justin pension:access_age"] == 60
    assert items["pension:Justin pension:drawdown"] is True


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


def test_property_workspace_reconciles_purchase_liquidity_rent_and_final_wealth() -> None:
    service = _service()
    workspace = service.property_decision()
    included = run_scenario(
        service.baseline.configuration,
        AdvisorScenario("Included", ScenarioOverride()),
    )
    excluded = run_scenario(
        service.baseline.configuration,
        AdvisorScenario("Excluded", ScenarioOverride(include_planned_rental_properties=False)),
    )

    assert (
        _comparison(workspace.evidence, "g002-liquidity").baseline_value
        == included.metrics.liquid_assets_at_life_expectancy
    )
    assert (
        _comparison(workspace.evidence, "g002-liquidity").scenario_value
        == excluded.metrics.liquid_assets_at_life_expectancy
    )
    assert (
        _comparison(workspace.evidence, "g002-net-worth").baseline_value
        == included.metrics.final_net_worth
    )
    assert (
        _comparison(workspace.evidence, "g002-net-worth").scenario_value
        == excluded.metrics.final_net_worth
    )
    purchase = next(item for item in workspace.evidence if item.evidence_id == "g002-purchase")
    assert purchase.value == Decimal("200000")  # type: ignore[union-attr]
    assert any(
        isinstance(item, TimelineEvidence) and item.evidence_id == "g002-property-series"
        for item in workspace.evidence
    )


def test_property_workspace_exposes_exact_bridge_and_assumption_evidence() -> None:
    workspace = _service().property_decision()
    evidence = {item.evidence_id: item for item in workspace.evidence}

    assert _metric(workspace.evidence, "g002-liquid-difference").value == Decimal(
        "596126.105942835067950553996"
    )
    assert _metric(workspace.evidence, "g002-after-tax-surplus").value == Decimal(
        "54954.6640896000000"
    )
    assert _metric(workspace.evidence, "g002-funding-preserved").value == Decimal(
        "719090.5094259550025333971644"
    )
    assert _metric(workspace.evidence, "g002-funding-order-growth").value == Decimal(
        "22080.9324272800654171568316"
    )
    rent_growth = evidence["g002-rent-growth"]
    appreciation = evidence["g002-appreciation"]
    assert isinstance(rent_growth, AssumptionEvidence)
    assert isinstance(appreciation, AssumptionEvidence)
    assert rent_growth.value == Decimal("0.02")
    assert appreciation.value == Decimal("0.03")


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


def test_employer_equity_exposes_concentration_denominator_and_protected_outcome() -> None:
    workspace = _service().employer_equity()
    evidence = {item.evidence_id: item for item in workspace.evidence}
    concentration = _comparison(workspace.evidence, "g003-concentration")
    denominator = evidence["g003-denominator"]

    assert concentration.baseline_value == Decimal("0.1375742688860239128304175150")
    assert concentration.scenario_value == Decimal("0.8795543048907487566337885495")
    assert isinstance(denominator, AssumptionEvidence)
    assert denominator.value == "Cash + taxable investments + employer equity"
    assert denominator.source == "RFC-010 investable-assets definition"
    assert _comparison(workspace.evidence, "g003-final-worth").scenario_value == Decimal(
        "12687376.37280836126030839548"
    )


def test_employer_equity_evidence_separates_concentration_from_wealth() -> None:
    workspace = _service().employer_equity()
    concentration = _comparison(workspace.evidence, "g003-concentration")
    final_worth = _comparison(workspace.evidence, "g003-final-worth")
    growth = next(item for item in workspace.evidence if item.evidence_id == "g003-growth")

    assert concentration.purpose is EvidencePurpose.TRADE_OFF
    assert final_worth.purpose is EvidencePurpose.COMPARISON
    assert isinstance(growth, AssumptionEvidence)
    assert concentration.evidence_id in workspace.evidence[0].citations  # type: ignore[union-attr]
    assert final_worth.evidence_id in workspace.evidence[0].citations  # type: ignore[union-attr]


def test_employer_equity_selected_policy_refreshes_evidence_without_mutating_baseline() -> None:
    service = _service()
    before = service.baseline.configuration.model_dump_json()
    retain = service.employer_equity(focus_sell_on_vest=False)
    sell = service.employer_equity(focus_sell_on_vest=True)

    assert dict(retain.provenance.scenario_overrides) == {"sell_on_vest": "false"}
    assert dict(sell.provenance.scenario_overrides) == {"sell_on_vest": "true"}
    assert "retain path is selected" in retain.evidence[0].text.casefold()  # type: ignore[union-attr]
    assert "sell on vest path is selected" in sell.evidence[0].text.casefold()  # type: ignore[union-attr]
    assert retain.provenance.result_fingerprint != sell.provenance.result_fingerprint
    assert service.baseline.configuration.model_dump_json() == before


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


def test_spending_input_is_today_money_and_first_retirement_value_is_nominal() -> None:
    service = _service()
    target = Decimal("120000")
    workspace = service.higher_spending(target)
    scenario = run_scenario(
        service.baseline.configuration,
        AdvisorScenario("Spending basis", ScenarioOverride(target_retirement_spending=target)),
    )
    basis = next(
        item
        for item in workspace.evidence
        if isinstance(item, AssumptionEvidence) and item.evidence_id == "g004-input-basis"
    )

    assert basis.value == target
    assert "today's money" in basis.label
    assert (
        _comparison(workspace.evidence, "g004-spending").scenario_value
        == scenario.metrics.first_retirement_spending
    )
    assert scenario.metrics.first_retirement_spending == target * Decimal("1.02") ** 6


def test_higher_spending_exposes_trajectory_funding_and_protected_outcome() -> None:
    workspace = _service().higher_spending(Decimal("100000"))
    evidence = {item.evidence_id: item for item in workspace.evidence}
    baseline = evidence["g004-liquid-baseline-series"]
    explored = evidence["g004-liquid-scenario-series"]
    milestones = evidence["g004-funding-milestones"]

    assert isinstance(baseline, TimelineEvidence)
    assert isinstance(explored, TimelineEvidence)
    assert len(baseline.points) == len(explored.points)
    assert baseline.points[-1].value == Decimal("4344368.266927997250165882396")
    assert explored.points[-1].value == Decimal("2927641.022946419129284394956")
    assert _comparison(workspace.evidence, "g004-final-worth").scenario_value == Decimal(
        "4413924.629759393112014262271"
    )
    assert isinstance(milestones, TableEvidence)
    assert (
        "Private-pension income begins",
        2032,
        "Reduces the remaining spending gap",
    ) in milestones.rows
    assert ("State Pension begins", 2038, "Adds another recurring-income source") in milestones.rows


def test_higher_spending_funding_order_is_explicit_and_evidence_scoped() -> None:
    workspace = _service().higher_spending(Decimal("100000"))
    funding = next(item for item in workspace.evidence if item.evidence_id == "g004-funding-order")

    assert isinstance(funding, AssumptionEvidence)
    assert funding.value == "Cash, then taxable investments, then retained employer equity"
    assert set(workspace.evidence[0].citations) == {  # type: ignore[union-attr]
        "g004-spending",
        "g004-liquid",
    }


def test_temporary_multi_year_spending_is_an_explicit_limitation() -> None:
    workspace = _service().higher_spending(Decimal("100000"), temporary_years=5)

    assert any(isinstance(item, LimitationEvidence) for item in workspace.evidence)
    assert not any(isinstance(item, ComparisonEvidence) for item in workspace.evidence)
    assert "not currently supported" in repr(workspace.evidence).casefold()


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


def test_cash_bridge_reconciles_direct_movements_for_pre_retirement_and_retirement() -> None:
    for year in (2027, 2032):
        workspace = _service().cash_decline(year)
        statement = next(
            item for item in workspace.evidence if isinstance(item, FinancialStatementEvidence)
        )
        increases = sum((value for _, value in statement.cash_increases), Decimal("0"))
        decreases = sum((value for _, value in statement.cash_decreases), Decimal("0"))

        assert statement.opening_cash + increases - decreases == statement.closing_cash


def test_cash_selected_year_refreshes_all_causal_evidence() -> None:
    service = _service()
    purchase_year = service.cash_decline(2027)
    retirement_year = service.cash_decline(2032)
    purchase_statement = next(
        item for item in purchase_year.evidence if isinstance(item, FinancialStatementEvidence)
    )
    retirement_statement = next(
        item for item in retirement_year.evidence if isinstance(item, FinancialStatementEvidence)
    )

    assert purchase_year.title == "What changed my cash in 2027?"
    assert "cash rises" in purchase_year.evidence[0].text.casefold()  # type: ignore[union-attr]
    assert "pre-retirement" in purchase_year.evidence[0].text.casefold()  # type: ignore[union-attr]
    assert dict(purchase_statement.cash_decreases)["Property purchase"] == Decimal("200000")
    assert retirement_year.title == "What changed my cash in 2032?"
    assert "cash falls" in retirement_year.evidence[0].text.casefold()  # type: ignore[union-attr]
    assert dict(retirement_statement.cash_decreases)["Cash used for spending"] == Decimal(
        "51709.0555320018444800"
    )
    assert retirement_statement.opening_cash == Decimal("1826630.7781896000000")
    assert retirement_statement.closing_cash == Decimal("1774921.7226575981555200")


@pytest.mark.parametrize(
    ("year", "employed", "required_text", "forbidden_text"),
    [
        (2027, True, "pre-retirement", "cover retirement spending"),
        (2032, False, "retirement spending", "pre-retirement"),
        (2035, False, "retirement spending", "pre-retirement"),
    ],
)
def test_cash_explanation_respects_actual_retirement_status(
    year: int,
    employed: bool,
    required_text: str,
    forbidden_text: str,
) -> None:
    workspace = _service().cash_decline(year)
    statement = next(
        item for item in workspace.evidence if isinstance(item, FinancialStatementEvidence)
    )
    answer = workspace.evidence[0]

    assert statement.employed is employed
    assert required_text in answer.text.casefold()  # type: ignore[union-attr]
    assert forbidden_text not in answer.text.casefold()  # type: ignore[union-attr]


def test_cash_decline_is_causal_and_requires_no_data_collection() -> None:
    workspace = _service().cash_decline(2032)
    answer = workspace.evidence[0]

    assert isinstance(answer, NarrativeEvidence)
    assert "opening cash" in answer.text.casefold()
    assert "closing cash" in answer.text.casefold()
    assert "question" not in repr(workspace).casefold()
    assert workspace.proposed_update is None


def test_cash_decline_narrative_matches_positive_private_pension_evidence() -> None:
    workspace = _service().cash_decline(2032)
    answer = workspace.evidence[0]
    statement = next(
        item for item in workspace.evidence if isinstance(item, FinancialStatementEvidence)
    )
    private_pension = dict(statement.inflows)["Private pension income"]

    assert private_pension > 0
    assert isinstance(answer, NarrativeEvidence)
    assert "private-pension income" in answer.text.casefold()
    assert "remainder comes from cash" in answer.text.casefold()
    assert "pensions continue to grow" not in answer.text.casefold()
    assert "pensions are not used" not in answer.text.casefold()


def test_live_display_formatting_hides_decimal_tails_without_mutating_evidence() -> None:
    value = Decimal("1732584.981918750000")
    workspace = _service().retire_earlier(58)
    comparison = _comparison(workspace.evidence, "g001-net-worth")
    exact = comparison.scenario_value

    assert format_display_value(value, "EUR") == "€1,732,585"
    assert format_table_value(value, "Modelled value") == "€1,732,585"
    assert "981918750000" not in format_table_value(value, "Modelled value")
    assert comparison.scenario_value == exact
    assert isinstance(comparison.scenario_value, Decimal)


def test_live_default_evidence_is_answer_first_and_dense_detail_is_secondary() -> None:
    workspace = _service().retire_earlier(58)
    primary, details, supporting = _evidence_groups(workspace.evidence)

    assert isinstance(primary[0], NarrativeEvidence)
    assert primary[0].purpose is EvidencePurpose.ANSWER
    assert len(primary) <= 3
    assert details
    assert supporting


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


def test_normal_streamlit_experience_hides_engineering_modes_and_provenance() -> None:
    app = AppTest.from_file(str(ROOT / "experience" / "app.py")).run(timeout=30)
    app.button(key="wos-recent-g-005").click().run(timeout=30)
    assert not app.exception
    rendered = "\n".join(markdown.value for markdown in app.markdown)
    forbidden = (
        "Mock Experience",
        "Live Deterministic Experience",
        "ScenarioOverride",
        "WorkspaceSpec",
        "fingerprint",
        "v0.2",
        "recovery",
    )
    assert all(term not in rendered for term in forbidden)
    assert "What changed my cash in 2032?" in rendered
    assert {item.label for item in app.expander} == {"About this projection"}


def _service() -> LiveExperienceService:
    return LiveExperienceService.from_example(ROOT)


def _comparison(evidence: tuple[object, ...], evidence_id: str) -> ComparisonEvidence:
    item = next(
        candidate
        for candidate in evidence
        if isinstance(candidate, ComparisonEvidence) and candidate.evidence_id == evidence_id
    )
    return item


def _metric(evidence: tuple[object, ...], evidence_id: str) -> MetricEvidence:
    item = next(
        candidate
        for candidate in evidence
        if isinstance(candidate, MetricEvidence) and candidate.evidence_id == evidence_id
    )
    return item
