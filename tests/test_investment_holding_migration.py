"""Regression invariants for canonical ordinary taxable-investment holdings."""

from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from engine.assets import InvestmentHolding
from engine.config import load_configuration
from engine.config.models import InvestmentConfig
from engine.reporting import (
    AdvisorScenario,
    ScenarioOverride,
    annual_financial_statement,
    run_scenario,
)
from engine.simulation import project_annually

ROOT = Path(__file__).resolve().parents[1]


def test_example_household_uses_one_canonical_holding_without_value_drift() -> None:
    """The former EUR 300k aggregate is represented once as one ETF holding."""
    config = load_configuration((ROOT / "data/example_household.yaml").read_text())

    assert len(config.investments.holdings) == 1
    assert config.investments.holdings[0].asset_type.value == "ETF"
    assert config.investments.holdings[0].current_value == Decimal("300000")
    assert config.investments.taxable_investment_value == Decimal("300000")
    assert "etf_value" not in type(config.investments).model_fields
    assert "etf_value" not in config.investments.model_dump()


def test_legacy_etf_input_migrates_to_holdings_as_input_compatibility_only() -> None:
    """Legacy fields are consumed by the adapter and do not survive as balances."""
    config = load_configuration((ROOT / "tests/fixtures/legacy_household.yaml").read_text())

    assert config.investments.taxable_investment_value == Decimal("150000")
    assert config.investments.taxable_investment_growth_rate == Decimal("0.05")
    assert config.investments.holdings[0].holding_id == "legacy-etf"
    assert set(config.investments.model_dump()) == {
        "cash_balance",
        "holdings",
        "taxable_investment_growth_rate",
    }


def test_legacy_and_canonical_values_cannot_be_combined() -> None:
    """Competing balances are rejected rather than added together."""
    with pytest.raises(ValidationError, match="cannot be combined"):
        InvestmentConfig.model_validate(
            {
                "cash_balance": "10",
                "etf_value": "20",
                "etf_growth_rate": "0.05",
                "holdings": [],
                "taxable_investment_growth_rate": "0.05",
            }
        )


def test_canonical_and_legacy_projection_paths_have_identical_financial_outputs() -> None:
    """Migration changes representation only, not any annual financial output."""
    legacy_text = (ROOT / "tests/fixtures/legacy_household.yaml").read_text()
    canonical_text = legacy_text.replace(
        "  etf_value: 150000\n  etf_growth_rate: 0.05",
        """  taxable_investment_growth_rate: 0.05
  holdings:
    - holding_id: legacy-etf
      name: Legacy ETF holding
      asset_type: ETF
      current_value: 150000""",
    )

    legacy_projection = project_annually(load_configuration(legacy_text))
    canonical_projection = project_annually(load_configuration(canonical_text))

    assert legacy_projection == canonical_projection
    assert legacy_projection[0].taxable_investment_value == Decimal("157500.00")
    assert legacy_projection[-1].liquid_assets == canonical_projection[-1].liquid_assets
    assert legacy_projection[-1].net_worth == canonical_projection[-1].net_worth


def test_holdings_feed_investable_assets_without_real_estate_or_pensions() -> None:
    """The concentration denominator uses the holding-derived taxable balance."""
    config = load_configuration((ROOT / "data/example_household.yaml").read_text())
    first_year = project_annually(config)[0]
    expected_denominator = (
        first_year.cash_balance + first_year.taxable_investment_value + first_year.amazon_value
    )

    assert first_year.amazon_concentration == first_year.amazon_value / expected_denominator
    assert first_year.pension_value > 0
    assert first_year.property_value == 0
    assert config.primary_residence is not None
    assert config.primary_residence.equity > 0
    assert expected_denominator < first_year.net_worth + config.primary_residence.equity


def test_diversified_etf_is_denominator_only_and_employer_equity_is_not_duplicated() -> None:
    """ETF capital dilutes employer concentration but is never its numerator."""
    config = load_configuration((ROOT / "data/example_household.yaml").read_text())
    first_year = project_annually(config)[0]

    assert all(holding.security_identifier is None for holding in config.investments.holdings)
    assert first_year.amazon_concentration < (
        first_year.amazon_value / (first_year.cash_balance + first_year.amazon_value)
    )
    assert config.investments.taxable_investment_value == sum(
        (holding.current_value for holding in config.investments.holdings),
        start=Decimal("0"),
    )


def test_multiple_holding_types_project_as_one_unchanged_aggregate_bucket() -> None:
    """The engine sums every ordinary holding before applying the shared growth rate."""
    config = load_configuration((ROOT / "data/example_household.yaml").read_text())
    first = config.investments.holdings[0].model_copy(update={"current_value": Decimal("100000")})
    second = InvestmentHolding.model_validate(
        {
            "holding_id": "individual-equity",
            "name": "Named shares",
            "asset_type": "INDIVIDUAL_EQUITY",
            "current_value": Decimal("200000"),
            "security_identifier": "EXAMPLE",
        }
    )
    investments = config.investments.model_copy(update={"holdings": (first, second)})
    projection = project_annually(config.model_copy(update={"investments": investments}))

    assert investments.taxable_investment_value == Decimal("300000")
    assert projection[0].taxable_investment_value == Decimal("318000.00")


def test_g001_through_g005_protected_financial_outputs_do_not_change() -> None:
    """The structural migration preserves each existing goal's financial evidence."""
    config = load_configuration((ROOT / "data/example_household.yaml").read_text())

    def metrics(override: ScenarioOverride) -> tuple[Decimal, Decimal]:
        result = run_scenario(config, AdvisorScenario("Regression", override)).metrics
        return result.liquid_assets_at_life_expectancy, result.final_net_worth

    assert metrics(ScenarioOverride(retirement_age=58)) == (
        Decimal("3558394.190628218053650981280"),
        Decimal("5044677.797441192036380848595"),
    )
    assert metrics(ScenarioOverride()) == (
        Decimal("4344368.266927997250165882396"),
        Decimal("5830651.873740971232895749711"),
    )
    assert metrics(ScenarioOverride(include_planned_rental_properties=False)) == (
        Decimal("3748242.160985162182215328400"),
        Decimal("4582118.209398321291411714807"),
    )
    assert metrics(ScenarioOverride(sell_on_vest=False)) == (
        Decimal("11201092.76599538727757852816"),
        Decimal("12687376.37280836126030839548"),
    )
    assert metrics(ScenarioOverride(target_retirement_spending=Decimal("100000"))) == (
        Decimal("2927641.022946419129284394956"),
        Decimal("4413924.629759393112014262271"),
    )

    projection = project_annually(config)
    cash_statement = annual_financial_statement(projection, config, 2032)
    assert cash_statement.assets.trace.opening_cash == Decimal("1826630.7781896000000")
    assert cash_statement.funding.cash_used == Decimal("51709.0555320018444800")
    assert cash_statement.funding.taxable_investments_sold == Decimal("0E-16")
    assert cash_statement.assets.trace.closing_cash == Decimal("1774921.7226575981555200")
