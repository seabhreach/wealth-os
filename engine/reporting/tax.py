"""Presentation-ready tax explanations derived from completed projections only."""

from dataclasses import dataclass
from decimal import Decimal

from engine.config.models import PropertyOwnerConfig, WealthOsConfig
from engine.simulation import project_annually
from engine.simulation.owners import owner_age_in_year
from engine.simulation.projection import ProjectionYear
from engine.tax.models import PersonTaxResult

ZERO = Decimal("0")
ONE = Decimal("1")


@dataclass(frozen=True, slots=True)
class PersonTaxStatement:
    """A person-level explanation of already-calculated income and tax for one year."""

    person: str
    age: int
    rental_profit: Decimal
    private_pension_income: Decimal
    state_pension_income: Decimal
    result: PersonTaxResult


@dataclass(frozen=True, slots=True)
class AnnualTaxStatement:
    """A gross-to-net retirement statement suitable for dashboard rendering."""

    calendar_year: int
    enabled: bool
    gross_recurring_income: Decimal
    income_tax: Decimal
    usc: Decimal
    prsi: Decimal
    total_tax: Decimal
    net_recurring_income: Decimal
    cash_used: Decimal
    etf_units_sold: Decimal
    amazon_shares_sold: Decimal
    unfunded_amount: Decimal
    retirement_spending: Decimal
    after_tax_surplus: Decimal
    people: tuple[PersonTaxStatement, ...]

    @property
    def total_funding(self) -> Decimal:
        """Return the visible net funding bridge total."""
        return (
            self.net_recurring_income
            + self.cash_used
            + self.etf_units_sold
            + self.amazon_shares_sold
            + self.unfunded_amount
        )


@dataclass(frozen=True, slots=True)
class TaxOwnershipComparison:
    """One temporary ownership split compared against the saved baseline."""

    label: str
    shares: tuple[PropertyOwnerConfig, ...]
    rental_profit_by_person: tuple[tuple[str, Decimal], ...]
    income_tax: Decimal
    usc: Decimal
    prsi: Decimal
    total_tax: Decimal
    after_tax_rental_income: Decimal
    tax_change_vs_baseline: Decimal
    liquid_assets_at_life_expectancy: Decimal
    final_net_worth: Decimal


@dataclass(frozen=True, slots=True)
class BeforeAfterTaxComparison:
    """Same-input enabled and disabled comparison for one deterministic configuration."""

    gross_recurring_income: Decimal
    tax: Decimal
    net_recurring_income: Decimal
    liquid_funding_before_tax: Decimal
    liquid_funding_after_tax: Decimal
    final_liquid_assets_before_tax: Decimal
    final_liquid_assets_after_tax: Decimal
    final_net_worth_before_tax: Decimal
    final_net_worth_after_tax: Decimal


def annual_tax_statement(
    timeline: tuple[ProjectionYear, ...], config: WealthOsConfig, calendar_year: int
) -> AnnualTaxStatement:
    """Build a display-only tax statement from an already completed selected year."""
    year = next(row for row in timeline if row.calendar_year == calendar_year)
    if not year.tax_modelling_enabled or year.household_tax_result is None:
        return AnnualTaxStatement(
            calendar_year,
            False,
            year.gross_recurring_income,
            ZERO,
            ZERO,
            ZERO,
            ZERO,
            year.gross_recurring_income,
            year.cash_withdrawal,
            year.etf_withdrawal,
            year.amazon_withdrawal,
            year.unfunded_spending,
            year.annual_spending,
            ZERO,
            (),
        )
    private_income = _private_income_by_person(year, config)
    state_income = _state_income_by_person(year, config)
    rental_income = _rental_income_by_person(year, config)
    people = tuple(
        PersonTaxStatement(
            result.person,
            owner_age_in_year(config, result.person, year.calendar_year),
            rental_income[result.person],
            private_income[result.person],
            state_income[result.person],
            result,
        )
        for result in year.household_tax_result.per_person
    )
    return AnnualTaxStatement(
        year.calendar_year,
        True,
        year.gross_recurring_income,
        year.estimated_income_tax,
        year.estimated_usc,
        year.estimated_prsi,
        year.total_estimated_tax,
        year.net_recurring_income,
        year.cash_withdrawal,
        year.etf_withdrawal,
        year.amazon_withdrawal,
        year.unfunded_spending,
        year.annual_spending,
        year.after_tax_surplus,
        people,
    )


def tax_over_time(timeline: tuple[ProjectionYear, ...]) -> tuple[ProjectionYear, ...]:
    """Return retirement rows for charts without recalculating the simulation."""
    return tuple(year for year in timeline if not year.employed)


def before_after_tax_comparison(config: WealthOsConfig) -> BeforeAfterTaxComparison | None:
    """Run the existing engine once with tax disabled for an equal-input comparison."""
    if not config.tax.enabled:
        return None
    enabled = project_annually(config)
    disabled_config = config.model_copy(
        update={"tax": config.tax.model_copy(update={"enabled": False})}
    )
    disabled = project_annually(disabled_config)
    enabled_retirement = next(year for year in enabled if not year.employed)
    disabled_retirement = next(year for year in disabled if not year.employed)
    return BeforeAfterTaxComparison(
        enabled_retirement.gross_recurring_income,
        enabled_retirement.total_estimated_tax,
        enabled_retirement.net_recurring_income,
        disabled_retirement.withdrawal_amount,
        enabled_retirement.withdrawal_amount,
        disabled[-1].liquid_assets,
        enabled[-1].liquid_assets,
        disabled[-1].net_worth,
        enabled[-1].net_worth,
    )


def ownership_tax_comparisons(
    config: WealthOsConfig, property_name: str
) -> tuple[TaxOwnershipComparison, ...]:
    """Run five immutable owner-split scenarios; saved configuration is never changed."""
    if not config.tax.enabled:
        return ()
    property_index = next(
        index
        for index, property_config in enumerate(config.rental_properties)
        if property_config.name == property_name
    )
    owners = _people(config)
    if len(owners) != 2:
        return ()
    baseline = project_annually(config)
    baseline_year = next(year for year in baseline if not year.employed)
    splits = (Decimal("1"), Decimal("0.75"), Decimal("0.5"), Decimal("0.25"), ZERO)
    comparisons: list[TaxOwnershipComparison] = []
    for first_share in splits:
        shares = (
            PropertyOwnerConfig(person=owners[0], share=first_share),
            PropertyOwnerConfig(person=owners[1], share=ONE - first_share),
        )
        properties = list(config.rental_properties)
        properties[property_index] = properties[property_index].model_copy(
            update={"owners": shares}
        )
        scenario_config = config.model_copy(update={"rental_properties": tuple(properties)})
        scenario = project_annually(scenario_config)
        year = next(row for row in scenario if not row.employed)
        statement = annual_tax_statement(scenario, scenario_config, year.calendar_year)
        comparisons.append(
            TaxOwnershipComparison(
                label=f"{first_share:.0%} {owners[0]} / {ONE - first_share:.0%} {owners[1]}",
                shares=shares,
                rental_profit_by_person=tuple(
                    (person.person, person.rental_profit) for person in statement.people
                ),
                income_tax=year.estimated_income_tax,
                usc=year.estimated_usc,
                prsi=year.estimated_prsi,
                total_tax=year.total_estimated_tax,
                after_tax_rental_income=year.rental_income - year.total_estimated_tax,
                tax_change_vs_baseline=year.total_estimated_tax - baseline_year.total_estimated_tax,
                liquid_assets_at_life_expectancy=scenario[-1].liquid_assets,
                final_net_worth=scenario[-1].net_worth,
            )
        )
    return tuple(comparisons)


def tax_advisor_insights(config: WealthOsConfig) -> tuple[str, ...]:
    """Return evidence-based tax observations sourced from deterministic projections."""
    comparison = before_after_tax_comparison(config)
    if comparison is None:
        return ("Tax modelling disabled. Enable it on Inputs to compare gross and net income.",)
    ownership = (
        ownership_tax_comparisons(config, config.rental_properties[0].name)
        if config.rental_properties
        else ()
    )
    final_liquid_assets_reduction = (
        comparison.final_liquid_assets_before_tax - comparison.final_liquid_assets_after_tax
    )
    insights = [
        "Estimated tax increases first-retirement-year liquid funding by "
        f"{comparison.liquid_funding_after_tax - comparison.liquid_funding_before_tax:.0f} EUR.",
        "Tax reduces final liquid assets by approximately "
        f"{final_liquid_assets_reduction:.0f} "
        "EUR under the current deterministic assumptions.",
        "The model excludes CGT on ETF and Amazon sales, so after-tax results may be overstated.",
    ]
    if ownership:
        spread = max(item.total_tax for item in ownership) - min(
            item.total_tax for item in ownership
        )
        insights.append(
            "The modelled first-year household tax difference across the displayed ownership "
            f"assumptions is approximately {spread:.0f} EUR."
        )
    return tuple(insights)


def _people(config: WealthOsConfig) -> tuple[str, ...]:
    return tuple(dict.fromkeys(pension.owner for pension in config.pensions))


def _private_income_by_person(year: ProjectionYear, config: WealthOsConfig) -> dict[str, Decimal]:
    incomes = {person: ZERO for person in _people(config)}
    for pension, withdrawal in zip(
        config.pensions, year.pension_withdrawal_by_pension, strict=True
    ):
        incomes[pension.owner] += withdrawal
    return incomes


def _state_income_by_person(year: ProjectionYear, config: WealthOsConfig) -> dict[str, Decimal]:
    incomes = {person: ZERO for person in _people(config)}
    offset = year.calendar_year - config.assumptions.start_year
    for pension in config.state_pensions:
        if (
            pension.enabled
            and owner_age_in_year(config, pension.owner, year.calendar_year) >= pension.start_age
        ):
            incomes[pension.owner] += (
                pension.annual_amount * (ONE + config.assumptions.inflation_rate) ** offset
                if pension.inflation_linked
                else pension.annual_amount
            )
    return incomes


def _rental_income_by_person(year: ProjectionYear, config: WealthOsConfig) -> dict[str, Decimal]:
    incomes = {person: ZERO for person in _people(config)}
    for property_config in config.rental_properties:
        if property_config.purchase_year > year.calendar_year:
            continue
        opening_year = max(property_config.purchase_year, config.assumptions.start_year)
        rent = property_config.annual_net_rent * (ONE + config.assumptions.inflation_rate) ** (
            year.calendar_year - opening_year
        )
        for owner in property_config.owners:
            incomes[owner.person] += rent * owner.share
    return incomes
