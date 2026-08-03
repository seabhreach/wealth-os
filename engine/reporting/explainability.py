"""Plain-English reporting and annual traceability for completed projections."""

from dataclasses import dataclass
from decimal import Decimal

from engine.config.models import WealthOsConfig
from engine.simulation.projection import ProjectionYear

ZERO = Decimal("0")
ONE = Decimal("1")


@dataclass(frozen=True, slots=True)
class AnnualCalculationTrace:
    """Existing annual projection values arranged as an auditable opening-to-closing trace."""

    calendar_year: int
    opening_cash: Decimal
    opening_etf_value: Decimal
    opening_amazon_shares: Decimal
    opening_amazon_value: Decimal
    opening_pension_value: Decimal
    opening_property_value: Decimal
    annual_savings: Decimal
    etf_growth_amount: Decimal
    amazon_growth_amount: Decimal
    rsu_shares_vested: Decimal
    rsu_sale_proceeds: Decimal
    rental_income: Decimal
    private_pension_income: Decimal
    state_pension_income: Decimal
    total_estimated_tax: Decimal
    pension_growth_amount: Decimal
    pension_contribution_amount: Decimal
    property_purchase_cost: Decimal
    property_appreciation: Decimal
    retirement_spending: Decimal
    cash_withdrawal: Decimal
    etf_withdrawal: Decimal
    amazon_withdrawal: Decimal
    unfunded_spending: Decimal
    closing_cash: Decimal
    closing_etf_value: Decimal
    closing_amazon_shares: Decimal
    closing_amazon_value: Decimal
    closing_pension_value: Decimal
    closing_property_value: Decimal
    closing_net_worth: Decimal


def annual_calculation_trace(
    timeline: tuple[ProjectionYear, ...], config: WealthOsConfig, calendar_year: int
) -> AnnualCalculationTrace:
    """Return a reporting trace for one completed row without changing the projection."""
    index = next(
        (position for position, year in enumerate(timeline) if year.calendar_year == calendar_year),
        None,
    )
    if index is None:
        raise ValueError(f"Calendar year {calendar_year} is outside the projection")
    closing = timeline[index]
    opening = timeline[index - 1] if index > 0 else None
    opening_cash = opening.cash_balance if opening is not None else config.investments.cash_balance
    opening_etf = opening.etf_value if opening is not None else config.investments.etf_value
    opening_amazon_shares = (
        opening.amazon_shares if opening is not None else config.amazon_rsus.vested_shares
    )
    opening_amazon_value = (
        opening.amazon_value
        if opening is not None
        else (
            config.amazon_rsus.vested_shares
            * config.amazon_rsus.share_price_usd
            * config.amazon_rsus.eur_usd_exchange_rate
        )
    )
    opening_pension = opening.pension_value if opening is not None else ZERO
    opening_property = opening.property_value if opening is not None else ZERO
    property_purchase_cost = sum(
        (
            property_config.purchase_price
            for property_config in config.rental_properties
            if property_config.purchase_year == closing.calendar_year
            and property_config.purchase_year > config.assumptions.start_year
        ),
        start=ZERO,
    )
    rsu_shares_vested = config.amazon_rsus.annual_grant_shares if closing.employed else ZERO
    price_before_growth = (
        config.amazon_rsus.share_price_usd
        * (ONE + config.amazon_rsus.annual_growth_rate) ** index
        * config.amazon_rsus.eur_usd_exchange_rate
    )
    rsu_sale_proceeds = (
        rsu_shares_vested * price_before_growth if config.amazon_rsus.sell_on_vest else ZERO
    )
    pension_contributions = (
        sum((pension.annual_contribution for pension in config.pensions), start=ZERO)
        if index > 0 and closing.employed
        else ZERO
    )
    retained_vesting_value = (
        ZERO
        if config.amazon_rsus.sell_on_vest
        else rsu_shares_vested
        * (closing.amazon_value / closing.amazon_shares if closing.amazon_shares != ZERO else ZERO)
    )
    return AnnualCalculationTrace(
        calendar_year=closing.calendar_year,
        opening_cash=opening_cash,
        opening_etf_value=opening_etf,
        opening_amazon_shares=opening_amazon_shares,
        opening_amazon_value=opening_amazon_value,
        opening_pension_value=opening_pension,
        opening_property_value=opening_property,
        annual_savings=closing.annual_savings,
        etf_growth_amount=closing.etf_value + closing.etf_withdrawal - opening_etf,
        amazon_growth_amount=(
            closing.amazon_value
            + closing.amazon_withdrawal
            - opening_amazon_value
            - retained_vesting_value
        ),
        rsu_shares_vested=rsu_shares_vested,
        rsu_sale_proceeds=rsu_sale_proceeds,
        rental_income=closing.rental_income,
        private_pension_income=closing.private_pension_income,
        state_pension_income=closing.state_pension_income,
        total_estimated_tax=closing.total_estimated_tax,
        pension_growth_amount=closing.pension_value - opening_pension - pension_contributions,
        pension_contribution_amount=pension_contributions,
        property_purchase_cost=property_purchase_cost,
        property_appreciation=closing.property_value - opening_property - property_purchase_cost,
        retirement_spending=closing.annual_spending,
        cash_withdrawal=closing.cash_withdrawal,
        etf_withdrawal=closing.etf_withdrawal,
        amazon_withdrawal=closing.amazon_withdrawal,
        unfunded_spending=closing.unfunded_spending,
        closing_cash=closing.cash_balance,
        closing_etf_value=closing.etf_value,
        closing_amazon_shares=closing.amazon_shares,
        closing_amazon_value=closing.amazon_value,
        closing_pension_value=closing.pension_value,
        closing_property_value=closing.property_value,
        closing_net_worth=closing.net_worth,
    )


def retirement_funding_explanation(year: ProjectionYear) -> str:
    """Describe an existing retirement row's funding sources without recalculation."""
    return (
        f"Your spending target is funded by rental income and {year.withdrawal_amount} "
        "withdrawn from liquid assets in the order cash, ETFs, then Amazon."
    )


def preserved_wealth_warning(year: ProjectionYear) -> str | None:
    """Flag when total wealth remains but no liquid assets are available for spending."""
    if year.liquid_assets == ZERO and year.net_worth > ZERO:
        return (
            "Most remaining wealth is held in pensions or property and is not currently used to "
            "fund spending."
        )
    return None
