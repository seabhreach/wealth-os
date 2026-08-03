"""Baseline-versus-scenario retirement reporting derived from completed projections."""

from dataclasses import dataclass
from decimal import Decimal

from engine.reporting.retirement import RetirementReadinessSummary

ComparisonValue = Decimal | int | bool | None


@dataclass(frozen=True, slots=True)
class RetirementComparisonMetric:
    """One labelled baseline-versus-what-if outcome without financial recalculation."""

    label: str
    baseline: ComparisonValue
    what_if: ComparisonValue
    difference: Decimal | int | None


@dataclass(frozen=True, slots=True)
class RetirementComparison:
    """Retirement scenario comparison derived from two reporting summaries."""

    baseline_age: int
    what_if_age: int
    metrics: tuple[RetirementComparisonMetric, ...]
    interpretation: str


def compare_retirement_readiness(
    baseline: RetirementReadinessSummary, what_if: RetirementReadinessSummary
) -> RetirementComparison:
    """Compare two completed retirement summaries without changing calculation semantics."""
    metrics = (
        _integer_metric("Retirement age", baseline.retirement_age, what_if.retirement_age),
        _integer_metric(
            "First retirement year", baseline.first_retirement_year, what_if.first_retirement_year
        ),
        RetirementComparisonMetric(
            "Retirement ready", baseline.retirement_ready, what_if.retirement_ready, None
        ),
        _optional_year_metric(
            "First unfunded year", baseline.first_unfunded_year, what_if.first_unfunded_year
        ),
        _decimal_metric(
            "Liquid assets at retirement",
            baseline.liquid_assets_at_retirement,
            what_if.liquid_assets_at_retirement,
        ),
        _decimal_metric(
            "Liquid assets at life expectancy",
            baseline.liquid_assets_at_life_expectancy,
            what_if.liquid_assets_at_life_expectancy,
        ),
        _decimal_metric(
            "Final pension value",
            baseline.pension_value_at_life_expectancy,
            what_if.pension_value_at_life_expectancy,
        ),
        _decimal_metric(
            "Final property value",
            baseline.property_value_at_life_expectancy,
            what_if.property_value_at_life_expectancy,
        ),
        _decimal_metric(
            "Final net worth",
            baseline.net_worth_at_life_expectancy,
            what_if.net_worth_at_life_expectancy,
        ),
    )
    return RetirementComparison(
        baseline_age=baseline.retirement_age,
        what_if_age=what_if.retirement_age,
        metrics=metrics,
        interpretation=_comparison_interpretation(baseline, what_if),
    )


def _comparison_interpretation(
    baseline: RetirementReadinessSummary, what_if: RetirementReadinessSummary
) -> str:
    """Describe funding change using only supplied reporting outcomes."""
    if what_if.first_unfunded_year is not None:
        baseline_text = (
            "no unfunded year under the baseline"
            if baseline.first_unfunded_year is None
            else f"{baseline.first_unfunded_year} under the baseline"
        )
        return (
            "The what-if plan first becomes unfunded in "
            f"{what_if.first_unfunded_year}, compared with {baseline_text}."
        )
    liquid_difference = (
        what_if.liquid_assets_at_life_expectancy - baseline.liquid_assets_at_life_expectancy
    )
    direction = "higher" if liquid_difference >= Decimal("0") else "lower"
    return (
        "The what-if plan remains fully funded through life expectancy, with final liquid assets "
        f"{direction} than the baseline."
    )


def _decimal_metric(label: str, baseline: Decimal, what_if: Decimal) -> RetirementComparisonMetric:
    """Build a currency comparison metric."""
    return RetirementComparisonMetric(label, baseline, what_if, what_if - baseline)


def _integer_metric(label: str, baseline: int, what_if: int) -> RetirementComparisonMetric:
    """Build an integer comparison metric."""
    return RetirementComparisonMetric(label, baseline, what_if, what_if - baseline)


def _optional_year_metric(
    label: str, baseline: int | None, what_if: int | None
) -> RetirementComparisonMetric:
    """Build a comparison metric for an optional year without inventing a numeric delta."""
    difference = what_if - baseline if what_if is not None and baseline is not None else None
    return RetirementComparisonMetric(label, baseline, what_if, difference)
