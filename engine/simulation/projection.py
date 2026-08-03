"""Deterministic annual timeline projection for Task 2."""

from dataclasses import dataclass
from decimal import Decimal

from engine.config.models import WealthOsConfig
from engine.simulation.amazon import apply_amazon_rsus
from engine.simulation.cash_etf import apply_cash_and_etf_growth
from engine.simulation.pensions import PensionBalance, apply_pension_growth
from engine.simulation.properties import apply_rental_properties
from engine.simulation.retirement import apply_retirement_withdrawals
from engine.tax.models import HouseholdTaxResult

ZERO = Decimal("0")
ONE = Decimal("1")


@dataclass(frozen=True, slots=True)
class ProjectionYear:
    """The household's balances and cashflow state for one calendar year."""

    calendar_year: int
    age: int
    employed: bool
    salary: Decimal
    annual_savings: Decimal
    cash_balance: Decimal
    etf_value: Decimal
    amazon_shares: Decimal
    amazon_value: Decimal
    amazon_concentration: Decimal
    pension_value: Decimal
    pension_values: tuple[PensionBalance, ...]
    property_value: Decimal
    property_count: int
    rental_income: Decimal
    state_pension_income: Decimal
    private_pension_income: Decimal
    tax_modelling_enabled: bool
    gross_rental_profit: Decimal
    gross_private_pension_income: Decimal
    gross_state_pension_income: Decimal
    gross_recurring_income: Decimal
    household_tax_result: HouseholdTaxResult | None
    estimated_income_tax: Decimal
    estimated_usc: Decimal
    estimated_prsi: Decimal
    total_estimated_tax: Decimal
    net_recurring_income: Decimal
    effective_tax_rate: Decimal
    spending_gap_after_tax: Decimal
    after_tax_surplus: Decimal
    pension_withdrawal_by_pension: tuple[Decimal, ...]
    total_pension_withdrawal: Decimal
    pension_accessible: bool
    pension_income_available: Decimal
    annual_spending: Decimal
    withdrawal_amount: Decimal
    cash_withdrawal: Decimal
    etf_withdrawal: Decimal
    amazon_withdrawal: Decimal
    unfunded_spending: Decimal
    retirement_target_met: bool
    liquid_assets: Decimal
    net_worth: Decimal

    def as_table_row(self) -> dict[str, int | bool | Decimal | str]:
        """Return a table-compatible representation for the dashboard."""
        return {
            "calendar_year": self.calendar_year,
            "age": self.age,
            "employed": self.employed,
            "salary": self.salary,
            "annual_savings": self.annual_savings,
            "cash_balance": self.cash_balance,
            "etf_value": self.etf_value,
            "amazon_shares": self.amazon_shares,
            "amazon_value": self.amazon_value,
            "amazon_concentration": self.amazon_concentration,
            "pension_value": self.pension_value,
            "pension_values": "; ".join(
                f"{pension_balance.owner}: {pension_balance.value}"
                for pension_balance in self.pension_values
            ),
            "property_value": self.property_value,
            "property_count": self.property_count,
            "rental_income": self.rental_income,
            "state_pension_income": self.state_pension_income,
            "private_pension_income": self.private_pension_income,
            "tax_modelling_enabled": self.tax_modelling_enabled,
            "gross_recurring_income": self.gross_recurring_income,
            "total_estimated_tax": self.total_estimated_tax,
            "net_recurring_income": self.net_recurring_income,
            "total_pension_withdrawal": self.total_pension_withdrawal,
            "annual_spending": self.annual_spending,
            "withdrawal_amount": self.withdrawal_amount,
            "cash_withdrawal": self.cash_withdrawal,
            "etf_withdrawal": self.etf_withdrawal,
            "amazon_withdrawal": self.amazon_withdrawal,
            "unfunded_spending": self.unfunded_spending,
            "retirement_target_met": self.retirement_target_met,
            "liquid_assets": self.liquid_assets,
            "net_worth": self.net_worth,
        }


def project_annually(configuration: WealthOsConfig) -> tuple[ProjectionYear, ...]:
    """Create annual projection rows through life expectancy with cash and ETF growth."""
    household = configuration.household
    assumptions = configuration.assumptions
    investments = configuration.investments

    amazon_value = (
        configuration.amazon_rsus.vested_shares
        * configuration.amazon_rsus.share_price_usd
        * configuration.amazon_rsus.eur_usd_exchange_rate
    )
    pension_value = ZERO
    property_value = sum(
        (property_config.current_value for property_config in configuration.rental_properties),
        start=ZERO,
    )
    rental_income = sum(
        (property_config.annual_net_rent for property_config in configuration.rental_properties),
        start=ZERO,
    )
    net_worth = (
        investments.cash_balance
        + investments.etf_value
        + amazon_value
        + pension_value
        + property_value
    )

    timeline = [
        _build_projection_year(
            configuration=configuration,
            calendar_year=assumptions.start_year + year_offset,
            age=household.current_age + year_offset,
            cash_balance=investments.cash_balance,
            etf_value=investments.etf_value,
            amazon_value=amazon_value,
            pension_value=pension_value,
            property_value=property_value,
            rental_income=rental_income,
            net_worth=net_worth,
            year_offset=year_offset,
        )
        for year_offset in range(household.life_expectancy - household.current_age + 1)
    ]
    cash_and_etf_projection = apply_cash_and_etf_growth(timeline, configuration)
    amazon_projection = apply_amazon_rsus(tuple(cash_and_etf_projection), configuration)
    property_projection = apply_rental_properties(amazon_projection, configuration)
    pension_projection = apply_pension_growth(property_projection, configuration)
    return apply_retirement_withdrawals(pension_projection, configuration)


def _build_projection_year(
    *,
    configuration: WealthOsConfig,
    calendar_year: int,
    age: int,
    cash_balance: Decimal,
    etf_value: Decimal,
    amazon_value: Decimal,
    pension_value: Decimal,
    property_value: Decimal,
    rental_income: Decimal,
    net_worth: Decimal,
    year_offset: int,
) -> ProjectionYear:
    """Build a static-balance row with employment and spending status."""
    employed = age < configuration.household.planned_retirement_age
    salary = configuration.employment.salary if employed else ZERO
    annual_savings = configuration.employment.annual_savings if employed else ZERO
    amazon_concentration = amazon_value / net_worth if net_worth != ZERO else ZERO

    return ProjectionYear(
        calendar_year=calendar_year,
        age=age,
        employed=employed,
        salary=salary,
        annual_savings=annual_savings,
        cash_balance=cash_balance,
        etf_value=etf_value,
        amazon_shares=configuration.amazon_rsus.vested_shares,
        amazon_value=amazon_value,
        amazon_concentration=amazon_concentration,
        pension_value=pension_value,
        pension_values=(),
        property_value=property_value,
        property_count=0,
        rental_income=rental_income,
        state_pension_income=ZERO,
        private_pension_income=ZERO,
        tax_modelling_enabled=configuration.tax.enabled,
        gross_rental_profit=ZERO,
        gross_private_pension_income=ZERO,
        gross_state_pension_income=ZERO,
        gross_recurring_income=ZERO,
        household_tax_result=None,
        estimated_income_tax=ZERO,
        estimated_usc=ZERO,
        estimated_prsi=ZERO,
        total_estimated_tax=ZERO,
        net_recurring_income=ZERO,
        effective_tax_rate=ZERO,
        spending_gap_after_tax=ZERO,
        after_tax_surplus=ZERO,
        pension_withdrawal_by_pension=(),
        total_pension_withdrawal=ZERO,
        pension_accessible=False,
        pension_income_available=ZERO,
        annual_spending=ZERO,
        withdrawal_amount=ZERO,
        cash_withdrawal=ZERO,
        etf_withdrawal=ZERO,
        amazon_withdrawal=ZERO,
        unfunded_spending=ZERO,
        retirement_target_met=True,
        liquid_assets=cash_balance + etf_value + amazon_value,
        net_worth=net_worth,
    )
