"""Focused reconciliation contracts for the G-002 property comparison."""

from decimal import Decimal
from pathlib import Path

from engine.config import load_configuration
from engine.reporting import (
    AdvisorScenario,
    ScenarioOverride,
    reconcile_property_scenarios,
    run_scenario,
)

ROOT = Path(__file__).resolve().parents[1]


def test_planned_property_reconciliation_matches_completed_scenarios() -> None:
    config = load_configuration((ROOT / "data" / "example_household.yaml").read_text())
    included = run_scenario(config, AdvisorScenario("Included", ScenarioOverride()))
    excluded = run_scenario(
        config,
        AdvisorScenario("Excluded", ScenarioOverride(include_planned_rental_properties=False)),
    )
    result = reconcile_property_scenarios(included, excluded, config.rental_properties[0])

    assert result.purchase_year == 2027
    assert result.purchase_price == Decimal("200000")
    assert result.purchase_year_liquid_effect == Decimal("-184000")
    assert result.configured_annual_net_rent == Decimal("16000")
    assert result.final_liquid_assets_difference == (
        included.metrics.liquid_assets_at_life_expectancy
        - excluded.metrics.liquid_assets_at_life_expectancy
    )
    assert result.final_property_value_difference == included.metrics.final_property_value
    assert result.final_net_worth_difference == (
        result.final_liquid_assets_difference + result.final_property_value_difference
    )
    assert result.cumulative_modelled_rent > result.purchase_price
    assert result.cumulative_liquid_funding_preserved > Decimal("0")
