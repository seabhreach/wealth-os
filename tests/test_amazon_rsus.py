"""Tests for the pure Amazon RSU simulation stage."""

from decimal import Decimal
from pathlib import Path

from engine.config import load_configuration
from engine.simulation import apply_amazon_rsus, project_annually

EXAMPLE_CONFIGURATION = Path("tests/fixtures/legacy_household.yaml")


def test_sell_on_vest_adds_proceeds_to_cash_without_retaining_granted_shares() -> None:
    """Sell-on-vest keeps the original holding and accumulates pre-growth sale proceeds."""
    configuration = load_configuration(EXAMPLE_CONFIGURATION.read_text(encoding="utf-8"))

    first_year, second_year = project_annually(configuration)[:2]

    assert first_year.amazon_shares == Decimal("100")
    assert first_year.amazon_value == Decimal("21000")
    assert first_year.cash_balance == Decimal("80000")
    assert second_year.amazon_shares == Decimal("100")
    assert second_year.amazon_value == Decimal("22050")
    assert second_year.cash_balance == Decimal("110250")
    assert first_year.amazon_concentration == first_year.amazon_value / first_year.net_worth


def test_hold_strategy_retains_newly_vested_shares() -> None:
    """Holding RSUs increases the share count and does not add vest proceeds to cash."""
    yaml_text = EXAMPLE_CONFIGURATION.read_text(encoding="utf-8").replace(
        "sell_on_vest: true", "sell_on_vest: false"
    )

    first_year, second_year = project_annually(load_configuration(yaml_text))[:2]

    assert first_year.amazon_shares == Decimal("125")
    assert first_year.amazon_value == Decimal("26250")
    assert first_year.cash_balance == Decimal("75000")
    assert second_year.amazon_shares == Decimal("150")
    assert second_year.amazon_value == Decimal("33075")


def test_zero_share_price_growth_preserves_share_price() -> None:
    """A zero RSU growth rate leaves retained-share value at the current share price."""
    yaml_text = (
        EXAMPLE_CONFIGURATION.read_text(encoding="utf-8")
        .replace("annual_growth_rate: 0.05", "annual_growth_rate: 0", 1)
        .replace("sell_on_vest: true", "sell_on_vest: false")
    )

    first_year, second_year = project_annually(load_configuration(yaml_text))[:2]

    assert first_year.amazon_value == Decimal("25000")
    assert second_year.amazon_value == Decimal("30000")


def test_negative_share_price_growth_reduces_value() -> None:
    """A negative RSU growth rate is applied once in every projection year."""
    yaml_text = EXAMPLE_CONFIGURATION.read_text(encoding="utf-8").replace(
        "annual_growth_rate: 0.05", "annual_growth_rate: -0.10", 1
    )

    first_year, second_year = project_annually(load_configuration(yaml_text))[:2]

    assert first_year.amazon_value == Decimal("18000")
    assert second_year.amazon_value == Decimal("16200")


def test_rsu_stage_is_pure_and_projection_is_deterministic() -> None:
    """The stage returns a new tuple without changing its input or future runs."""
    configuration = load_configuration(EXAMPLE_CONFIGURATION.read_text(encoding="utf-8"))
    original_projection = project_annually(configuration)

    updated_projection = apply_amazon_rsus(original_projection, configuration)

    assert updated_projection is not original_projection
    assert original_projection == project_annually(configuration)
    assert project_annually(configuration) == project_annually(configuration)
