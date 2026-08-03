"""Tests for reporting-only deterministic Advisor Mode scenarios."""

from pathlib import Path

from engine.config import load_configuration
from engine.config.models import WealthOsConfig
from engine.reporting import (
    advisor_insights,
    apply_override,
    default_scenarios,
    retirement_age_explorer,
    run_default_scenarios,
    sensitivity_analysis,
)


def _configuration() -> WealthOsConfig:
    """Return the immutable approved baseline configuration."""
    return load_configuration(Path("data/example_household.yaml").read_text(encoding="utf-8"))


def test_default_scenarios_are_reproducible_and_leave_baseline_unchanged() -> None:
    """Temporary strategy overrides never mutate the saved configuration."""
    configuration = _configuration()
    results = run_default_scenarios(configuration)

    assert tuple(result.metrics.scenario.name for result in results) == tuple(
        scenario.name for scenario in default_scenarios(configuration)
    )
    assert results[0].projection[-1].net_worth > 0
    assert configuration.household.planned_retirement_age == 60
    assert configuration.amazon_rsus.sell_on_vest is True
    assert (
        apply_override(configuration, default_scenarios(configuration)[4].override) != configuration
    )
    assert run_default_scenarios(configuration) == results


def test_default_strategy_set_covers_retirement_rsus_property_and_spending() -> None:
    """Every requested advisor comparison is represented by a completed scenario result."""
    results = run_default_scenarios(_configuration())
    by_name = {result.metrics.scenario.name: result.metrics for result in results}

    assert by_name["Retire now"].retirement_age == 54
    assert by_name["Retire one year earlier"].retirement_age == 59
    assert by_name["Retire one year later"].retirement_age == 61
    assert (
        by_name["Retain Amazon RSUs"].maximum_amazon_concentration
        > by_name["Baseline"].maximum_amazon_concentration
    )
    assert by_name["No rental property"].final_property_value == 0
    assert (
        by_name["Lower spending"].first_retirement_spending
        < by_name["Baseline"].first_retirement_spending
    )


def test_advisor_insights_and_explorers_remain_evidence_based() -> None:
    """Insights avoid investment recommendations and explorers return deterministic metrics."""
    configuration = _configuration()
    results = run_default_scenarios(configuration)
    insights = advisor_insights(results)

    assert insights
    assert all("guaranteed" not in insight.lower() for insight in insights)
    assert (
        min(result.metrics.retirement_age for result in retirement_age_explorer(configuration))
        == 54
    )
    assert len(sensitivity_analysis(configuration)) == 12
