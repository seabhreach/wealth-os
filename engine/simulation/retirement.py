"""Retirement spending and fixed-order withdrawal stage."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

from engine.config.models import WealthOsConfig
from engine.simulation.owners import owner_age_in_year
from engine.simulation.pensions import PensionBalance
from engine.tax.calculator import calculate_household_tax
from engine.tax.models import HouseholdTaxInput, HouseholdTaxResult, PersonTaxInput
from engine.tax.rules import TaxRules, index_tax_rules, load_tax_rules

if TYPE_CHECKING:
    from engine.simulation.projection import ProjectionYear


ZERO = Decimal("0")
ONE = Decimal("1")


@dataclass(frozen=True, slots=True)
class WithdrawalBreakdown:
    """The amounts withdrawn from each permitted retirement asset class."""

    cash: Decimal
    etf: Decimal
    amazon: Decimal


class TaxSimulationError(ValueError):
    """Raised when enabled tax modelling cannot be evaluated safely."""


def apply_retirement_withdrawals(
    timeline: tuple[ProjectionYear, ...], config: WealthOsConfig
) -> tuple[ProjectionYear, ...]:
    """Return a new timeline after inflation-adjusted retirement spending and withdrawals.

    Cash, ETF holdings, then retained Amazon shares cover the spending gap in that order.
    Rental income already in cash reduces the gap and is never added a second time.
    """
    cash_adjustment = ZERO
    previous_etf_value = ZERO
    previous_pension_balances: tuple[PensionBalance, ...] = ()
    actual_amazon_shares = ZERO
    previous_upstream_amazon_shares = ZERO
    updated_timeline: list[ProjectionYear] = []
    base_tax_rules = _load_enabled_tax_rules(config)

    for index, projection_year in enumerate(timeline):
        cash_before_withdrawal = projection_year.cash_balance + cash_adjustment
        etf_before_withdrawal = (
            projection_year.etf_value
            if index == 0
            else previous_etf_value * (ONE + config.investments.etf_growth_rate)
        )
        actual_amazon_shares = _amazon_shares_before_withdrawal(
            index=index,
            projection_year=projection_year,
            actual_amazon_shares=actual_amazon_shares,
            previous_upstream_amazon_shares=previous_upstream_amazon_shares,
        )
        amazon_share_price = _amazon_share_price(projection_year)
        annual_spending = _annual_spending(projection_year, config)
        state_pension_by_owner = _state_pension_income_by_owner(projection_year, config)
        state_pension_income = sum(state_pension_by_owner.values(), start=ZERO)
        pension_balances_before_drawdown = _pension_balances_before_drawdown(
            index, previous_pension_balances, projection_year, config
        )
        pension_balances, pension_income_available, pension_withdrawals = _apply_pension_drawdown(
            pension_balances_before_drawdown,
            projection_year,
            config,
            annual_spending - projection_year.rental_income - state_pension_income,
        )
        private_pension_income = sum(pension_withdrawals, start=ZERO)
        tax_result = _calculate_projection_tax(
            projection_year=projection_year,
            config=config,
            base_rules=base_tax_rules,
            pension_withdrawals=pension_withdrawals,
            state_pension_by_owner=state_pension_by_owner,
        )
        gross_recurring_income = (
            projection_year.rental_income + state_pension_income + private_pension_income
        )
        if tax_result is None:
            total_estimated_tax = ZERO
            net_recurring_income = gross_recurring_income
            spending_gap = max(annual_spending - gross_recurring_income, ZERO)
            after_tax_surplus = ZERO
        else:
            total_estimated_tax = tax_result.total_tax
            net_recurring_income = gross_recurring_income - total_estimated_tax
            spending_gap = max(annual_spending - net_recurring_income, ZERO)
            after_tax_surplus = max(net_recurring_income - annual_spending, ZERO)
        withdrawals = _withdraw_in_order(
            spending_gap=spending_gap,
            cash_balance=cash_before_withdrawal,
            etf_value=etf_before_withdrawal,
            amazon_shares=actual_amazon_shares,
            amazon_share_price=amazon_share_price,
        )

        cash_balance = cash_before_withdrawal - withdrawals.cash
        etf_value = etf_before_withdrawal - withdrawals.etf
        if amazon_share_price != ZERO:
            actual_amazon_shares -= withdrawals.amazon / amazon_share_price
        amazon_value = actual_amazon_shares * amazon_share_price
        withdrawal_amount = withdrawals.cash + withdrawals.etf + withdrawals.amazon
        unfunded_spending = spending_gap - withdrawal_amount
        liquid_assets = cash_balance + etf_value + amazon_value
        pension_value = sum((balance.value for balance in pension_balances), start=ZERO)
        net_worth = liquid_assets + pension_value + projection_year.property_value
        amazon_concentration = amazon_value / net_worth if net_worth != ZERO else ZERO

        updated_timeline.append(
            replace(
                projection_year,
                annual_spending=annual_spending,
                state_pension_income=state_pension_income,
                private_pension_income=private_pension_income,
                tax_modelling_enabled=config.tax.enabled,
                gross_rental_profit=projection_year.rental_income,
                gross_private_pension_income=private_pension_income,
                gross_state_pension_income=state_pension_income,
                gross_recurring_income=gross_recurring_income,
                household_tax_result=tax_result,
                estimated_income_tax=tax_result.total_income_tax if tax_result else ZERO,
                estimated_usc=tax_result.total_usc if tax_result else ZERO,
                estimated_prsi=tax_result.total_prsi if tax_result else ZERO,
                total_estimated_tax=total_estimated_tax,
                net_recurring_income=net_recurring_income,
                effective_tax_rate=tax_result.effective_rate if tax_result else ZERO,
                spending_gap_after_tax=spending_gap,
                after_tax_surplus=after_tax_surplus,
                pension_values=pension_balances,
                pension_value=pension_value,
                pension_withdrawal_by_pension=pension_withdrawals,
                total_pension_withdrawal=private_pension_income,
                pension_accessible=pension_income_available > ZERO,
                pension_income_available=pension_income_available,
                cash_balance=cash_balance,
                etf_value=etf_value,
                amazon_shares=actual_amazon_shares,
                amazon_value=amazon_value,
                amazon_concentration=amazon_concentration,
                withdrawal_amount=withdrawal_amount,
                cash_withdrawal=withdrawals.cash,
                etf_withdrawal=withdrawals.etf,
                amazon_withdrawal=withdrawals.amazon,
                unfunded_spending=unfunded_spending,
                retirement_target_met=unfunded_spending == ZERO,
                liquid_assets=liquid_assets,
                net_worth=net_worth,
            )
        )
        cash_adjustment -= withdrawals.cash
        previous_etf_value = etf_value
        previous_pension_balances = pension_balances
        previous_upstream_amazon_shares = projection_year.amazon_shares

    return tuple(updated_timeline)


def _annual_spending(projection_year: ProjectionYear, config: WealthOsConfig) -> Decimal:
    """Return zero before retirement or the start-year target inflated to this year."""
    if projection_year.employed:
        return ZERO

    year_offset = projection_year.calendar_year - config.assumptions.start_year
    return (
        config.assumptions.target_retirement_income
        * (ONE + config.assumptions.inflation_rate) ** year_offset
    )


def _state_pension_income(projection_year: ProjectionYear, config: WealthOsConfig) -> Decimal:
    """Return user-configured State Pension income, inflation linked from the projection start."""
    return sum(_state_pension_income_by_owner(projection_year, config).values(), start=ZERO)


def _load_enabled_tax_rules(config: WealthOsConfig) -> TaxRules | None:
    """Load rules once for an enabled run, failing rather than silently disabling tax."""
    if not config.tax.enabled:
        return None
    path = Path(config.tax.rules_file)
    if not path.is_file():
        raise TaxSimulationError(f"Tax rules file does not exist: {config.tax.rules_file}")
    try:
        return load_tax_rules(path)
    except (KeyError, OSError, TypeError, ValueError) as error:
        raise TaxSimulationError(
            f"Unable to load tax rules from {config.tax.rules_file}."
        ) from error


def _calculate_projection_tax(
    *,
    projection_year: ProjectionYear,
    config: WealthOsConfig,
    base_rules: TaxRules | None,
    pension_withdrawals: tuple[Decimal, ...],
    state_pension_by_owner: dict[str, Decimal],
) -> HouseholdTaxResult | None:
    """Return this retirement row's tax estimate from owner-specific recurring income."""
    if base_rules is None or projection_year.employed:
        return None

    private_income = {owner: ZERO for owner in _household_people(config)}
    for pension, withdrawal in zip(config.pensions, pension_withdrawals, strict=True):
        private_income[pension.owner] += withdrawal
    rental_income = _rental_profit_by_owner(projection_year, config)
    people = tuple(
        PersonTaxInput(
            person=owner,
            private_pension_income=private_income[owner],
            state_pension_income=state_pension_by_owner[owner],
            rental_profit=rental_income[owner],
            prsi_taxable_income=(
                (private_income[owner] if config.tax.pension_prsi_enabled else ZERO)
                + (rental_income[owner] if config.tax.rental_prsi_enabled else ZERO)
            ),
        )
        for owner in _household_people(config)
    )
    indexed_rules = (
        index_tax_rules(
            base_rules,
            projection_year.calendar_year - base_rules.tax_year,
            config.assumptions.inflation_rate,
        )
        if config.tax.index_future_rules_with_inflation
        else base_rules
    )
    prsi_rules = replace(
        indexed_rules,
        prsi_enabled=config.tax.pension_prsi_enabled or config.tax.rental_prsi_enabled,
    )
    return calculate_household_tax(
        HouseholdTaxInput(config.tax.assessment_basis, people), prsi_rules
    )


def _household_people(config: WealthOsConfig) -> tuple[str, ...]:
    """Return configuration-defined people in deterministic pension declaration order."""
    return tuple(dict.fromkeys(pension.owner for pension in config.pensions))


def _rental_profit_by_owner(
    projection_year: ProjectionYear, config: WealthOsConfig
) -> dict[str, Decimal]:
    """Allocate configured net rent by explicit beneficial ownership shares."""
    profits = {owner: ZERO for owner in _household_people(config)}
    for property_config in config.rental_properties:
        if property_config.purchase_year > projection_year.calendar_year:
            continue
        opening_year = max(property_config.purchase_year, config.assumptions.start_year)
        annual_rent = property_config.annual_net_rent * (
            ONE + config.assumptions.inflation_rate
        ) ** (projection_year.calendar_year - opening_year)
        for owner in property_config.owners:
            profits[owner.person] += annual_rent * owner.share
    return profits


def _state_pension_income_by_owner(
    projection_year: ProjectionYear, config: WealthOsConfig
) -> dict[str, Decimal]:
    """Return owner-specific State Pension income using each owner's chronological age."""
    years = projection_year.calendar_year - config.assumptions.start_year
    incomes = {owner: ZERO for owner in _household_people(config)}
    for pension in config.state_pensions:
        if (
            pension.enabled
            and owner_age_in_year(config, pension.owner, projection_year.calendar_year)
            >= pension.start_age
        ):
            incomes[pension.owner] += (
                pension.annual_amount * (ONE + config.assumptions.inflation_rate) ** years
                if pension.inflation_linked
                else pension.annual_amount
            )
    return incomes


def _pension_balances_before_drawdown(
    index: int,
    previous_balances: tuple[PensionBalance, ...],
    projection_year: ProjectionYear,
    config: WealthOsConfig,
) -> tuple[PensionBalance, ...]:
    """Carry actual post-withdrawal balances through subsequent growth and contributions."""
    if index == 0:
        return projection_year.pension_values
    balances: list[PensionBalance] = []
    for previous, pension in zip(previous_balances, config.pensions, strict=True):
        contribution = (
            pension.annual_contribution
            if projection_year.employed
            and owner_age_in_year(config, pension.owner, projection_year.calendar_year)
            < (pension.access_age or config.household.planned_retirement_age)
            else ZERO
        )
        balances.append(
            PensionBalance(
                previous.name,
                previous.owner,
                previous.value * (ONE + pension.annual_growth_rate) + contribution,
            )
        )
    return tuple(balances)


def _apply_pension_drawdown(
    balances_before_drawdown: tuple[PensionBalance, ...],
    projection_year: ProjectionYear,
    config: WealthOsConfig,
    income_gap: Decimal,
) -> tuple[tuple[PensionBalance, ...], Decimal, tuple[Decimal, ...]]:
    """Withdraw permitted pension income after growth/contributions, capped by the remaining gap."""
    remaining_gap = max(income_gap, ZERO)
    balances: list[PensionBalance] = []
    withdrawals: list[Decimal] = []
    available_total = ZERO
    for balance, pension in zip(balances_before_drawdown, config.pensions, strict=True):
        access_age = pension.access_age or config.household.planned_retirement_age
        owner_age = owner_age_in_year(config, pension.owner, projection_year.calendar_year)
        permitted = (
            min(
                balance.value * pension.annual_drawdown_rate,
                pension.maximum_annual_withdrawal
                if pension.maximum_annual_withdrawal is not None
                else balance.value,
                balance.value,
            )
            if pension.enabled_for_drawdown and owner_age >= access_age
            else ZERO
        )
        available_total += permitted
        withdrawal = min(permitted, remaining_gap)
        remaining_gap -= withdrawal
        balances.append(
            PensionBalance(balance.name, balance.owner, balance.value - withdrawal, withdrawal)
        )
        withdrawals.append(withdrawal)
    return tuple(balances), available_total, tuple(withdrawals)


def _amazon_shares_before_withdrawal(
    *,
    index: int,
    projection_year: ProjectionYear,
    actual_amazon_shares: Decimal,
    previous_upstream_amazon_shares: Decimal,
) -> Decimal:
    """Carry sold-share reductions forward while retaining upstream newly vested shares."""
    if index == 0:
        return projection_year.amazon_shares

    newly_retained_shares = projection_year.amazon_shares - previous_upstream_amazon_shares
    return actual_amazon_shares + newly_retained_shares


def _amazon_share_price(projection_year: ProjectionYear) -> Decimal:
    """Derive the current projected Amazon share price from upstream holdings."""
    if projection_year.amazon_shares == ZERO:
        return ZERO
    return projection_year.amazon_value / projection_year.amazon_shares


def _withdraw_in_order(
    *,
    spending_gap: Decimal,
    cash_balance: Decimal,
    etf_value: Decimal,
    amazon_shares: Decimal,
    amazon_share_price: Decimal,
) -> WithdrawalBreakdown:
    """Fund as much of the gap as possible from cash, ETF, then Amazon shares."""
    cash_withdrawal = min(cash_balance, spending_gap)
    remaining_gap = spending_gap - cash_withdrawal
    etf_withdrawal = min(etf_value, remaining_gap)
    remaining_gap -= etf_withdrawal
    amazon_value = amazon_shares * amazon_share_price
    amazon_withdrawal = min(amazon_value, remaining_gap)
    return WithdrawalBreakdown(
        cash=cash_withdrawal,
        etf=etf_withdrawal,
        amazon=amazon_withdrawal,
    )
