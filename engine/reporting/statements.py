"""Household-friendly retirement funding and asset-movement statements."""

from dataclasses import dataclass
from decimal import Decimal

from engine.config.models import WealthOsConfig
from engine.reporting.explainability import AnnualCalculationTrace, annual_calculation_trace
from engine.simulation.projection import ProjectionYear

ZERO = Decimal("0")


@dataclass(frozen=True, slots=True)
class AnnualFundingStatement:
    """Completed gross-to-net recurring income and liquid funding for one year."""

    rental_income: Decimal
    state_pension: Decimal
    private_pension_income: Decimal
    estimated_income_tax: Decimal
    estimated_usc: Decimal
    estimated_prsi: Decimal
    tax_modelling_enabled: bool
    cash_used: Decimal
    etf_units_sold: Decimal
    amazon_shares_sold: Decimal
    other_income: Decimal
    unfunded_amount: Decimal
    retirement_spending: Decimal

    @property
    def total_funding(self) -> Decimal:
        """Return net recurring income plus liquid funding and any explicit shortfall."""
        return sum(
            (
                self.rental_income,
                self.state_pension,
                self.private_pension_income,
                -self.estimated_income_tax,
                -self.estimated_usc,
                -self.estimated_prsi,
                self.cash_used,
                self.etf_units_sold,
                self.amazon_shares_sold,
                self.other_income,
                self.unfunded_amount,
            ),
            start=ZERO,
        )

    @property
    def surplus_or_deficit(self) -> Decimal:
        """Return funding less spending; rent above spending is retained as surplus."""
        return self.total_funding - self.retirement_spending


@dataclass(frozen=True, slots=True)
class AssetMovementStatement:
    """Opening-to-closing asset movements for the selected completed projection row."""

    trace: AnnualCalculationTrace
    amazon_shares_sold_on_vest: Decimal
    amazon_shares_sold_for_spending: Decimal
    amazon_retained_rsu_value: Decimal


@dataclass(frozen=True, slots=True)
class AnnualFinancialStatement:
    """A reporting-only annual household statement for a completed projection year."""

    calendar_year: int
    salary: Decimal
    funding: AnnualFundingStatement
    assets: AssetMovementStatement
    liquid_assets: Decimal
    net_worth: Decimal


def annual_financial_statement(
    timeline: tuple[ProjectionYear, ...], config: WealthOsConfig, calendar_year: int
) -> AnnualFinancialStatement:
    """Build a user-facing statement solely from projection rows and trace reporting outputs."""
    year = next((row for row in timeline if row.calendar_year == calendar_year), None)
    if year is None:
        raise ValueError(f"Calendar year {calendar_year} is outside the projection")
    trace = annual_calculation_trace(timeline, config, calendar_year)
    funding = AnnualFundingStatement(
        rental_income=year.rental_income,
        state_pension=year.state_pension_income,
        private_pension_income=year.private_pension_income,
        estimated_income_tax=year.estimated_income_tax,
        estimated_usc=year.estimated_usc,
        estimated_prsi=year.estimated_prsi,
        tax_modelling_enabled=year.tax_modelling_enabled,
        cash_used=year.cash_withdrawal,
        etf_units_sold=year.etf_withdrawal,
        amazon_shares_sold=year.amazon_withdrawal,
        other_income=ZERO,
        unfunded_amount=year.unfunded_spending,
        retirement_spending=year.annual_spending,
    )
    share_price = year.amazon_value / year.amazon_shares if year.amazon_shares != ZERO else ZERO
    shares_sold_for_spending = year.amazon_withdrawal / share_price if share_price != ZERO else ZERO
    return AnnualFinancialStatement(
        calendar_year=calendar_year,
        salary=year.salary,
        funding=funding,
        assets=AssetMovementStatement(
            trace=trace,
            amazon_shares_sold_on_vest=(
                trace.rsu_shares_vested if config.amazon_rsus.sell_on_vest else ZERO
            ),
            amazon_shares_sold_for_spending=shares_sold_for_spending,
            amazon_retained_rsu_value=(
                trace.closing_amazon_value
                + trace.amazon_withdrawal
                - trace.opening_amazon_value
                - trace.amazon_growth_amount
            ),
        ),
        liquid_assets=year.liquid_assets,
        net_worth=year.net_worth,
    )


def retirement_funding_narrative(statement: AnnualFinancialStatement) -> str:
    """Explain the selected statement's actual funding sources in plain English."""
    funding = statement.funding
    sources: list[str] = []
    if funding.rental_income:
        sources.append("rental income")
    if funding.cash_used:
        sources.append("cash reserves")
    if funding.etf_units_sold:
        sources.append("ETF sales")
    if funding.amazon_shares_sold:
        sources.append("Amazon share sales")
    if funding.unfunded_amount:
        return (
            f"In {statement.calendar_year}, rent and all permitted liquid assets are insufficient; "
            f"part of spending remains unfunded. Pensions and property remain untouched."
        )
    if not sources:
        return f"In {statement.calendar_year}, no retirement spending is required."
    return (
        f"In {statement.calendar_year}, retirement spending is funded by "
        f"{', '.join(sources)}. Pensions continue to grow and are not used in this model."
    )
