"""Deterministic, reporting-only retirement strategy comparisons for Advisor Mode."""

from dataclasses import dataclass
from decimal import Decimal

from engine.config.models import WealthOsConfig
from engine.reporting.retirement import RetirementReadinessSummary, summarize_retirement_readiness
from engine.simulation import project_annually
from engine.simulation.projection import ProjectionYear

ZERO = Decimal("0")
ONE = Decimal("1")


@dataclass(frozen=True, slots=True)
class ScenarioOverride:
    """Allowed temporary configuration changes for an in-memory advisor scenario."""

    retirement_age: int | None = None
    sell_on_vest: bool | None = None
    include_planned_rental_properties: bool | None = None
    target_retirement_spending: Decimal | None = None
    etf_growth_rate: Decimal | None = None
    amazon_growth_rate: Decimal | None = None
    inflation_rate: Decimal | None = None


@dataclass(frozen=True, slots=True)
class AdvisorScenario:
    """A reproducible named scenario made from one allowed override set."""

    name: str
    override: ScenarioOverride


@dataclass(frozen=True, slots=True)
class ScenarioMetrics:
    """Decision metrics calculated from one completed deterministic scenario projection."""

    scenario: AdvisorScenario
    retirement_age: int
    retirement_ready: bool
    first_unfunded_year: int | None
    liquid_assets_at_retirement: Decimal
    liquid_assets_at_life_expectancy: Decimal
    final_pension_value: Decimal
    final_property_value: Decimal
    final_amazon_value: Decimal
    final_net_worth: Decimal
    maximum_amazon_concentration: Decimal
    first_retirement_spending: Decimal
    first_retirement_rental_income: Decimal
    first_retirement_liquid_funding: Decimal
    years_fully_funded: int
    first_retirement_cash: Decimal
    first_retirement_amazon_value: Decimal
    first_retirement_required_funding: Decimal


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    """Scenario metrics and completed outputs retained for reporting-only comparisons."""

    metrics: ScenarioMetrics
    readiness: RetirementReadinessSummary
    projection: tuple[ProjectionYear, ...]


@dataclass(frozen=True, slots=True)
class SensitivityResult:
    """One one-variable deterministic sensitivity point."""

    variable: str
    label: str
    value: Decimal
    metrics: ScenarioMetrics


def default_scenarios(configuration: WealthOsConfig) -> tuple[AdvisorScenario, ...]:
    """Return the small, valid default strategy set for the loaded baseline."""
    household = configuration.household
    baseline_age = household.planned_retirement_age
    scenarios = [AdvisorScenario("Baseline", ScenarioOverride())]
    if household.current_age <= baseline_age:
        scenarios.append(AdvisorScenario("Retire now", ScenarioOverride(household.current_age)))
    if baseline_age - 1 >= household.current_age:
        scenarios.append(
            AdvisorScenario(
                "Retire one year earlier", ScenarioOverride(retirement_age=baseline_age - 1)
            )
        )
    scenarios.extend(
        (
            AdvisorScenario(
                "Retire one year later", ScenarioOverride(retirement_age=baseline_age + 1)
            ),
            AdvisorScenario("Retain Amazon RSUs", ScenarioOverride(sell_on_vest=False)),
            AdvisorScenario(
                "No rental property", ScenarioOverride(include_planned_rental_properties=False)
            ),
            AdvisorScenario(
                "Lower spending",
                ScenarioOverride(
                    target_retirement_spending=(
                        configuration.assumptions.target_retirement_income * Decimal("0.90")
                    )
                ),
            ),
        )
    )
    return tuple(scenarios)


def run_scenario(configuration: WealthOsConfig, scenario: AdvisorScenario) -> ScenarioResult:
    """Run one immutable temporary scenario through the existing deterministic engine."""
    scenario_configuration = apply_override(configuration, scenario.override)
    projection = project_annually(scenario_configuration)
    readiness = summarize_retirement_readiness(projection)
    retirement_year = next(year for year in projection if not year.employed)
    return ScenarioResult(
        metrics=ScenarioMetrics(
            scenario=scenario,
            retirement_age=retirement_year.age,
            retirement_ready=readiness.retirement_ready,
            first_unfunded_year=readiness.first_unfunded_year,
            liquid_assets_at_retirement=readiness.liquid_assets_at_retirement,
            liquid_assets_at_life_expectancy=readiness.liquid_assets_at_life_expectancy,
            final_pension_value=projection[-1].pension_value,
            final_property_value=projection[-1].property_value,
            final_amazon_value=projection[-1].amazon_value,
            final_net_worth=projection[-1].net_worth,
            maximum_amazon_concentration=max(
                (year.amazon_concentration for year in projection), default=ZERO
            ),
            first_retirement_spending=retirement_year.annual_spending,
            first_retirement_rental_income=retirement_year.rental_income,
            first_retirement_liquid_funding=retirement_year.withdrawal_amount,
            years_fully_funded=sum(
                1 for year in projection if not year.employed and year.retirement_target_met
            ),
            first_retirement_cash=retirement_year.cash_balance,
            first_retirement_amazon_value=retirement_year.amazon_value,
            first_retirement_required_funding=retirement_year.withdrawal_amount,
        ),
        readiness=readiness,
        projection=projection,
    )


def apply_override(configuration: WealthOsConfig, override: ScenarioOverride) -> WealthOsConfig:
    """Return a validated immutable copy containing only permitted temporary scenario changes."""
    household = configuration.household.model_copy(
        update={
            "planned_retirement_age": override.retirement_age
            if override.retirement_age is not None
            else configuration.household.planned_retirement_age
        }
    )
    investments = configuration.investments.model_copy(
        update={
            "etf_growth_rate": override.etf_growth_rate
            if override.etf_growth_rate is not None
            else configuration.investments.etf_growth_rate
        }
    )
    amazon = configuration.amazon_rsus.model_copy(
        update={
            "sell_on_vest": override.sell_on_vest
            if override.sell_on_vest is not None
            else configuration.amazon_rsus.sell_on_vest,
            "annual_growth_rate": override.amazon_growth_rate
            if override.amazon_growth_rate is not None
            else configuration.amazon_rsus.annual_growth_rate,
        }
    )
    assumptions = configuration.assumptions.model_copy(
        update={
            "target_retirement_income": override.target_retirement_spending
            if override.target_retirement_spending is not None
            else configuration.assumptions.target_retirement_income,
            "inflation_rate": override.inflation_rate
            if override.inflation_rate is not None
            else configuration.assumptions.inflation_rate,
        }
    )
    properties = (
        tuple(
            property_config
            for property_config in configuration.rental_properties
            if property_config.purchase_year <= configuration.assumptions.start_year
        )
        if override.include_planned_rental_properties is False
        else configuration.rental_properties
    )
    return configuration.model_copy(
        update={
            "household": household,
            "investments": investments,
            "amazon_rsus": amazon,
            "assumptions": assumptions,
            "rental_properties": properties,
        }
    )


def run_default_scenarios(configuration: WealthOsConfig) -> tuple[ScenarioResult, ...]:
    """Run the default report deterministically in its stable presentation order."""
    return tuple(
        run_scenario(configuration, scenario) for scenario in default_scenarios(configuration)
    )


def advisor_insights(results: tuple[ScenarioResult, ...]) -> tuple[str, ...]:
    """Generate evidence-based interpretations using only completed scenario metrics."""
    baseline = results[0].metrics
    insights: list[str] = []
    for result in results[1:]:
        metrics = result.metrics
        if metrics.scenario.name.startswith("Retire"):
            status = (
                "remains fully funded"
                if metrics.retirement_ready
                else (f"first becomes unfunded in {metrics.first_unfunded_year}")
            )
            liquid_assets_change = (
                metrics.liquid_assets_at_life_expectancy - baseline.liquid_assets_at_life_expectancy
            )
            insights.append(
                f"{metrics.scenario.name} {status} under these assumptions; final liquid assets "
                f"change by {liquid_assets_change:+.0f} EUR."
            )
        elif metrics.scenario.name == "Retain Amazon RSUs":
            insights.append(
                "Retaining all RSUs changes final net worth by "
                f"{metrics.final_net_worth - baseline.final_net_worth:+.0f} EUR and raises maximum "
                f"Amazon concentration to {metrics.maximum_amazon_concentration:.1%}."
            )
        elif metrics.scenario.name == "No rental property":
            rental_income_change = (
                metrics.first_retirement_rental_income - baseline.first_retirement_rental_income
            )
            insights.append(
                "Removing the planned rental property changes first-retirement rental income by "
                f"{rental_income_change:+.0f} EUR."
            )
    return tuple(insights)


def retirement_age_explorer(configuration: WealthOsConfig) -> tuple[ScenarioResult, ...]:
    """Compare the requested valid retirement ages using existing scenario execution."""
    baseline_age = configuration.household.planned_retirement_age
    candidate_ages = (
        configuration.household.current_age,
        baseline_age - 2,
        baseline_age - 1,
        baseline_age,
        baseline_age + 1,
        baseline_age + 3,
    )
    ages = tuple(
        dict.fromkeys(age for age in candidate_ages if age >= configuration.household.current_age)
    )
    return tuple(
        run_scenario(configuration, AdvisorScenario(f"Retire at {age}", ScenarioOverride(age)))
        for age in ages
    )


def sensitivity_analysis(configuration: WealthOsConfig) -> tuple[SensitivityResult, ...]:
    """Run small fixed one-variable deterministic sensitivity ranges around the baseline."""
    baseline = configuration.assumptions
    values = (
        ("ETF growth", "ETF growth", configuration.investments.etf_growth_rate, Decimal("0.02")),
        (
            "Amazon growth",
            "Amazon growth",
            configuration.amazon_rsus.annual_growth_rate,
            Decimal("0.05"),
        ),
        ("Inflation", "Inflation", baseline.inflation_rate, Decimal("0.01")),
    )
    results: list[SensitivityResult] = []
    for variable, label, base_value, delta in values:
        for value in (base_value - delta, base_value, base_value + delta):
            override = _sensitivity_override(variable, value)
            result = run_scenario(configuration, AdvisorScenario(f"{label} {value:.1%}", override))
            results.append(SensitivityResult(variable, label, value, result.metrics))
    for multiplier in (Decimal("0.90"), ONE, Decimal("1.10")):
        value = baseline.target_retirement_income * multiplier
        result = run_scenario(
            configuration,
            AdvisorScenario("Target spending", ScenarioOverride(target_retirement_spending=value)),
        )
        results.append(
            SensitivityResult("Target spending", "Target spending", value, result.metrics)
        )
    return tuple(results)


def _sensitivity_override(variable: str, value: Decimal) -> ScenarioOverride:
    """Create the permitted override corresponding to one sensitivity variable."""
    if variable == "ETF growth":
        return ScenarioOverride(etf_growth_rate=value)
    if variable == "Amazon growth":
        return ScenarioOverride(amazon_growth_rate=value)
    return ScenarioOverride(inflation_rate=value)
