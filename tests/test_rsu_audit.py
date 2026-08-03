"""Regression coverage for the baseline RSU and cash accumulation audit bridges."""

from decimal import Decimal
from pathlib import Path

from engine.config import load_configuration
from engine.reporting import RsuAuditSummary, summarize_rsu_audit
from engine.simulation import project_annually


def _audit() -> RsuAuditSummary:
    """Return the reporting-only audit for the released baseline configuration."""
    configuration = load_configuration(
        Path("data/example_household.yaml").read_text(encoding="utf-8")
    )
    return summarize_rsu_audit(project_annually(configuration), configuration)


def test_baseline_has_exactly_six_working_year_grants_sold_into_cash() -> None:
    """Ages 54 through 59 vest six grants; age 60 retirement does not vest another grant."""
    audit = _audit()

    assert audit.opening_vested_shares == Decimal("310")
    assert audit.annual_grant_shares == Decimal("800")
    assert audit.sell_on_vest is True
    assert audit.working_year_grants == 6
    assert sum(
        (row.shares_vested for row in audit.amazon_share_bridge), start=Decimal("0")
    ) == Decimal("4800")
    assert sum(
        (row.shares_sold_on_vest for row in audit.amazon_share_bridge), start=Decimal("0")
    ) == Decimal("4800")
    assert audit.amazon_share_bridge[6].shares_vested == Decimal("0")
    assert audit.amazon_share_bridge[6].closing_shares == Decimal("310")


def test_baseline_cash_and_share_bridges_reconcile_to_first_retirement_year() -> None:
    """Pre-retirement cash and share movements visibly explain the first retirement row."""
    audit = _audit()
    cash_rows = audit.cash_bridge
    first_retirement = cash_rows[-1]

    assert audit.cumulative_rsu_sale_proceeds == Decimal("1351676.114100000000")
    assert first_retirement.closing_cash == Decimal("1820896.9939791981555200")
    assert sum((row.annual_savings for row in cash_rows), start=Decimal("0")) == Decimal("120000")
    assert sum((row.rental_income for row in cash_rows), start=Decimal("0")) == Decimal(
        "100929.9354112000"
    )
    assert (
        cash_rows[0].opening_cash
        + audit.cumulative_annual_savings
        + audit.cumulative_rsu_sale_proceeds
        + audit.cumulative_rental_income
        + sum((row.other_cash_movement for row in cash_rows), start=Decimal("0"))
        - audit.cumulative_property_purchases
        - sum((row.cash_used_for_spending for row in cash_rows), start=Decimal("0"))
        == first_retirement.closing_cash
    )
    share_rows = audit.amazon_share_bridge[:7]
    assert (
        share_rows[0].opening_shares
        + sum((row.shares_vested for row in share_rows), start=Decimal("0"))
        - sum((row.shares_sold_on_vest for row in share_rows), start=Decimal("0"))
        - sum((row.shares_sold_for_spending for row in share_rows), start=Decimal("0"))
        == share_rows[-1].closing_shares
    )
    assert share_rows[-1].eur_amazon_value == Decimal("108352.3609462218750000")


def test_hold_strategy_retains_each_working_year_grant_in_the_share_bridge() -> None:
    """The audit exposes the alternate configured policy without changing the model's timing."""
    yaml_text = Path("data/example_household.yaml").read_text(encoding="utf-8")
    configuration = load_configuration(
        yaml_text.replace("sell_on_vest: true", "sell_on_vest: false")
    )
    audit = summarize_rsu_audit(project_annually(configuration), configuration)
    first_retirement_row = audit.amazon_share_bridge[6]

    assert first_retirement_row.closing_shares == Decimal("5110")
    assert sum(
        (row.shares_sold_on_vest for row in audit.amazon_share_bridge), start=Decimal("0")
    ) == Decimal("0")
