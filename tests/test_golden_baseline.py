"""Golden checkpoints and focused regression cases for the v0.1 example configuration."""

from decimal import Decimal
from pathlib import Path

from engine.config import load_configuration
from engine.reporting import summarize_retirement_readiness
from engine.simulation import project_annually

EXAMPLE_CONFIGURATION = Path("data/example_household.yaml")


def _example_yaml() -> str:
    """Return the documented baseline configuration text."""
    return EXAMPLE_CONFIGURATION.read_text(encoding="utf-8")


def test_golden_baseline_checkpoints() -> None:
    """The documented baseline produces stable, explainable deterministic checkpoints."""
    projection = project_annually(load_configuration(_example_yaml()))
    readiness = summarize_retirement_readiness(projection)
    first_retirement_year = next(year for year in projection if not year.employed)
    final_year = projection[-1]

    # The first projection row is an end-of-year row: 310 * USD 270 * EUR 0.92 * 1.05.
    assert projection[0].net_worth == Decimal("1817574.2000")
    assert projection[0].amazon_value == Decimal("80854.2000")
    assert first_retirement_year.calendar_year == 2032
    assert first_retirement_year.annual_spending == Decimal("90092.993541120000")
    assert first_retirement_year.rental_income == Decimal("17665.2928512000")
    assert first_retirement_year.withdrawal_amount == Decimal("51709.0555320018444800")
    assert readiness.retirement_ready is True
    assert final_year.liquid_assets == Decimal("5291173.968348116643592369726")
    assert final_year.pension_value == Decimal("833876.0484131591091963864071")
    assert final_year.property_value == Decimal("652407.5583998148735334809083")
    assert final_year.net_worth == Decimal("6777457.575161090626322237041")


def test_baseline_sells_newly_vested_amazon_shares_into_eur_cash() -> None:
    """The baseline's sell-on-vest policy retains only opening shares and adds EUR proceeds."""
    opening_year = project_annually(load_configuration(_example_yaml()))[0]

    assert opening_year.amazon_shares == Decimal("310")
    assert opening_year.cash_balance == Decimal("718720.00")


def test_baseline_opens_without_the_planned_property() -> None:
    """Current-position reporting excludes Ardfield Court until its 2027 cash purchase."""
    opening_year, purchase_year = project_annually(load_configuration(_example_yaml()))[:2]

    assert opening_year.property_value == Decimal("0")
    assert opening_year.property_count == 0
    assert purchase_year.property_value == Decimal("200000")
    assert purchase_year.property_count == 1
    assert purchase_year.rental_income == Decimal("16000")
    assert purchase_year.cash_balance == Decimal("763376.0000")


def test_amazon_usd_value_is_converted_to_eur() -> None:
    """Amazon USD holdings are converted before entering EUR balances and net worth."""
    yaml_text = (
        _example_yaml()
        .replace("annual_grant_shares: 800", "annual_grant_shares: 0")
        .replace("annual_growth_rate: 0.05", "annual_growth_rate: 0", 1)
    )

    opening_year = project_annually(load_configuration(yaml_text))[0]

    assert opening_year.amazon_value == Decimal("77004.00")
    assert opening_year.amazon_value != Decimal("83700")


def test_baseline_edge_case_regressions() -> None:
    """Critical zero-value and immediate-retirement variants remain deterministic and valid."""
    zero_properties = _example_yaml()
    property_section = zero_properties[
        zero_properties.index("rental_properties:") : zero_properties.index("assumptions:")
    ]
    zero_properties = zero_properties.replace(property_section, "rental_properties: []\n")
    zero_properties_projection = project_annually(load_configuration(zero_properties))

    zero_growth = (
        _example_yaml()
        .replace("etf_growth_rate: 0.06", "etf_growth_rate: 0")
        .replace("annual_growth_rate: 0.05", "annual_growth_rate: 0", 1)
        .replace("annual_grant_shares: 800", "annual_grant_shares: 0")
        .replace("inflation_rate: 0.02", "inflation_rate: 0")
    )
    zero_growth_projection = project_annually(load_configuration(zero_growth))

    immediate_retirement = _example_yaml().replace("current_age: 54", "current_age: 60")
    immediate_retirement_projection = project_annually(load_configuration(immediate_retirement))

    insufficient_assets = (
        zero_properties.replace("cash_balance: 500000", "cash_balance: 0")
        .replace("etf_value: 300000", "etf_value: 0")
        .replace("vested_shares: 310", "vested_shares: 0")
        .replace("annual_grant_shares: 800", "annual_grant_shares: 0")
        .replace("target_retirement_income: 80000", "target_retirement_income: 1000000")
    )
    insufficient_readiness = summarize_retirement_readiness(
        project_annually(load_configuration(insufficient_assets))
    )

    assert all(year.property_count == 0 for year in zero_properties_projection)
    assert zero_growth_projection[0].etf_value == Decimal("300000")
    assert zero_growth_projection[0].amazon_value == Decimal("77004.00")
    assert next(
        year for year in zero_growth_projection if not year.employed
    ).annual_spending == Decimal("80000")
    assert immediate_retirement_projection[0].employed is False
    assert immediate_retirement_projection[0].annual_spending == Decimal("80000")
    assert insufficient_readiness.retirement_ready is False
    assert insufficient_readiness.first_unfunded_year is not None
