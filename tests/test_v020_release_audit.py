"""End-to-end reconciliation and release audit coverage for the v0.2 baseline."""

from decimal import Decimal
from pathlib import Path

from dashboard.inputs import configuration_to_yaml
from engine.config import WealthOsConfig, load_configuration
from engine.reporting import (
    annual_calculation_trace,
    annual_tax_statement,
    ownership_tax_comparisons,
    run_default_scenarios,
)
from engine.simulation import project_annually
from engine.simulation.owners import owner_age_in_year

TOLERANCE = Decimal("0.00000000000000000001")


def _configuration() -> WealthOsConfig:
    return load_configuration(Path("data/example_household.yaml").read_text(encoding="utf-8"))


def _close(left: Decimal, right: Decimal) -> bool:
    return abs(left - right) <= TOLERANCE


def test_every_baseline_year_reconciles_balances_income_and_net_worth() -> None:
    """The complete released baseline obeys every published annual reconciliation."""
    configuration = _configuration()
    timeline = project_annually(configuration)
    for index, year in enumerate(timeline):
        trace = annual_calculation_trace(timeline, configuration, year.calendar_year)
        assert _close(
            trace.opening_cash
            + trace.annual_savings
            + trace.rsu_sale_proceeds
            + trace.rental_income
            - trace.property_purchase_cost
            - trace.cash_withdrawal,
            trace.closing_cash,
        )
        assert _close(
            trace.opening_etf_value + trace.etf_growth_amount - trace.etf_withdrawal,
            trace.closing_etf_value,
        )
        assert _close(
            year.net_worth,
            year.cash_balance
            + year.etf_value
            + year.amazon_value
            + year.pension_value
            + year.property_value,
        )
        assert _close(
            year.gross_recurring_income - year.total_estimated_tax,
            year.net_recurring_income,
        )
        if not year.employed:
            assert _close(
                year.net_recurring_income
                + year.withdrawal_amount
                + year.unfunded_spending
                - year.after_tax_surplus,
                year.annual_spending,
            )
        if index:
            previous = timeline[index - 1]
            for pension, previous_balance, current_balance, withdrawal in zip(
                configuration.pensions,
                previous.pension_values,
                year.pension_values,
                year.pension_withdrawal_by_pension,
                strict=True,
            ):
                contribution = (
                    pension.annual_contribution
                    if year.employed
                    and owner_age_in_year(configuration, pension.owner, year.calendar_year)
                    < (pension.access_age or configuration.household.planned_retirement_age)
                    else Decimal("0")
                )
                assert _close(
                    previous_balance.value * (Decimal("1") + pension.annual_growth_rate)
                    + contribution
                    - withdrawal,
                    current_balance.value,
                )


def test_release_checkpoints_preserve_owner_specific_income_timing() -> None:
    """Owner ages govern pension access and State Pension starts in the released baseline."""
    timeline = project_annually(_configuration())
    by_year = {year.calendar_year: year for year in timeline}
    assert by_year[2027].property_value == Decimal("200000")
    assert by_year[2032].private_pension_income > Decimal("0")
    assert by_year[2032].pension_withdrawal_by_pension[1] == Decimal("0")
    assert by_year[2035].pension_withdrawal_by_pension[1] > Decimal("0")
    assert by_year[2038].state_pension_income > Decimal("0")
    assert _close(
        by_year[2040].state_pension_income,
        by_year[2038].state_pension_income * Decimal("1.02") ** 2,
    )
    assert by_year[2041].state_pension_income > by_year[2040].state_pension_income


def test_tax_worked_examples_and_advisor_scenarios_remain_deterministic() -> None:
    """Tax examples, ownership comparisons, and ordinary scenarios keep the baseline immutable."""
    configuration = _configuration()
    baseline = project_annually(configuration)
    first_retirement = annual_tax_statement(baseline, configuration, 2032)
    assert first_retirement.total_tax == Decimal("4587.7352120018444800")
    assert first_retirement.people[1].state_pension_income == Decimal("0")
    assert first_retirement.people[0].result.usc_taxable == (
        first_retirement.people[0].private_pension_income + first_retirement.people[0].rental_profit
    )
    ownership = ownership_tax_comparisons(configuration, "Ardfield Court")
    assert [item.label for item in ownership] == [
        "100% Justin / 0% Wife",
        "75% Justin / 25% Wife",
        "50% Justin / 50% Wife",
        "25% Justin / 75% Wife",
        "0% Justin / 100% Wife",
    ]
    assert project_annually(configuration) == baseline
    assert run_default_scenarios(configuration) == run_default_scenarios(configuration)


def test_yaml_round_trip_preserves_tax_ownership_and_projection() -> None:
    """The released user workflow preserves Decimal ownership values and completed outputs."""
    configuration = _configuration()
    reloaded = load_configuration(configuration_to_yaml(configuration))
    assert reloaded == configuration
    assert project_annually(reloaded) == project_annually(configuration)
