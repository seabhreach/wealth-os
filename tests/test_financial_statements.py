"""Tests for reporting-only retirement income and asset movement statements."""

from decimal import Decimal
from pathlib import Path

from dashboard.components.formatting import (
    display_eur_value,
    display_reconciliation_adjustment,
    display_whole_value,
)
from engine.config import load_configuration
from engine.config.models import WealthOsConfig
from engine.reporting import annual_financial_statement, retirement_funding_narrative
from engine.simulation import project_annually
from engine.simulation.projection import ProjectionYear


def _baseline() -> tuple[WealthOsConfig, tuple[ProjectionYear, ...]]:
    """Return the completed documented projection without changing its calculation inputs."""
    config = load_configuration(Path("data/example_household.yaml").read_text(encoding="utf-8"))
    return config, project_annually(config)


def test_first_retirement_statement_reconciles_rent_and_cash_to_spending() -> None:
    """The first baseline retirement year explicitly records zero pension incomes and cash use."""
    config, timeline = _baseline()
    statement = annual_financial_statement(timeline, config, 2032)

    assert statement.funding.rental_income == Decimal("17665.2928512000")
    assert statement.funding.cash_used == Decimal("51709.0555320018444800")
    assert statement.funding.etf_units_sold == Decimal("0E-12")
    assert statement.funding.state_pension == Decimal("0")
    assert statement.funding.private_pension_income == Decimal("25306.38036992000000")
    assert statement.funding.total_funding == statement.funding.retirement_spending
    assert "cash reserves" in retirement_funding_narrative(statement)


def test_asset_movement_reconciles_cash_etfs_pensions_and_property() -> None:
    """The statement is a reporting view whose trace components reconcile closing balances."""
    config, timeline = _baseline()
    statement = annual_financial_statement(timeline, config, 2032)
    trace = statement.assets.trace

    assert (
        trace.opening_cash + trace.rsu_sale_proceeds + trace.rental_income - trace.cash_withdrawal
        == trace.closing_cash
    )
    assert (
        trace.opening_etf_value + trace.etf_growth_amount - trace.etf_withdrawal
        == trace.closing_etf_value
    )
    assert trace.opening_pension_value + trace.pension_growth_amount == trace.closing_pension_value
    assert (
        trace.opening_property_value + trace.property_appreciation == trace.closing_property_value
    )


def test_later_retirement_statement_preserves_pension_and_state_pension_exclusions() -> None:
    """Later statements retain the MVP's explicit zero-income pension and State Pension lines."""
    config, timeline = _baseline()
    statement = annual_financial_statement(timeline, config, 2043)

    assert statement.funding.state_pension > Decimal("0")
    assert statement.funding.private_pension_income > Decimal("0")
    assert "Pensions continue to grow" in retirement_funding_narrative(statement)


def test_displayed_statement_reconciliations_include_whole_euro_adjustments() -> None:
    """Every visible whole-euro equation sums exactly, including the documented cash adjustment."""
    config, timeline = _baseline()
    statement = annual_financial_statement(timeline, config, 2032)
    funding = statement.funding
    trace = statement.assets.trace

    equations = (
        (
            funding.total_funding,
            (
                funding.rental_income,
                funding.state_pension,
                funding.private_pension_income,
                funding.cash_used,
                funding.etf_units_sold,
                funding.amazon_shares_sold,
                funding.other_income,
                funding.unfunded_amount,
            ),
            (funding.estimated_income_tax, funding.estimated_usc, funding.estimated_prsi),
        ),
        (
            trace.closing_cash,
            (
                trace.opening_cash,
                trace.annual_savings,
                trace.rsu_sale_proceeds,
                trace.rental_income,
            ),
            (trace.property_purchase_cost, trace.cash_withdrawal),
        ),
        (
            trace.closing_etf_value,
            (trace.opening_etf_value, trace.etf_growth_amount),
            (trace.etf_withdrawal,),
        ),
        (
            trace.closing_amazon_value,
            (
                trace.opening_amazon_value,
                trace.amazon_growth_amount,
                statement.assets.amazon_retained_rsu_value,
            ),
            (trace.amazon_withdrawal,),
        ),
        (
            trace.closing_pension_value,
            (
                trace.opening_pension_value,
                trace.pension_growth_amount,
                trace.pension_contribution_amount,
            ),
            (),
        ),
        (
            trace.closing_property_value,
            (
                trace.opening_property_value,
                trace.property_purchase_cost,
                trace.property_appreciation,
            ),
            (),
        ),
    )
    for closing, additions, subtractions in equations:
        adjustment = display_reconciliation_adjustment(closing, additions, subtractions)
        visible_total = sum((display_eur_value(value) for value in additions), start=Decimal("0"))
        visible_total -= sum(
            (display_eur_value(value) for value in subtractions), start=Decimal("0")
        )
        assert visible_total + adjustment == display_eur_value(closing)

    cash_adjustment = display_reconciliation_adjustment(
        trace.closing_cash,
        (
            trace.opening_cash,
            trace.annual_savings,
            trace.rsu_sale_proceeds,
            trace.rental_income,
        ),
        (trace.property_purchase_cost, trace.cash_withdrawal),
    )
    assert cash_adjustment == Decimal("0")
    displayed_share_adjustment = display_whole_value(trace.closing_amazon_shares) - (
        display_whole_value(trace.opening_amazon_shares)
        + display_whole_value(trace.rsu_shares_vested)
        - display_whole_value(statement.assets.amazon_shares_sold_on_vest)
        - display_whole_value(statement.assets.amazon_shares_sold_for_spending)
    )
    assert display_whole_value(trace.opening_amazon_shares) + display_whole_value(
        trace.rsu_shares_vested
    ) - display_whole_value(statement.assets.amazon_shares_sold_on_vest) - display_whole_value(
        statement.assets.amazon_shares_sold_for_spending
    ) + displayed_share_adjustment == display_whole_value(trace.closing_amazon_shares)
