"""Reporting-only regression tests for the Task 3C tax presentation layer."""

from decimal import Decimal
from pathlib import Path

from dashboard.components.formatting import format_eur_cents
from engine.config import WealthOsConfig, load_configuration
from engine.reporting import (
    annual_tax_statement,
    before_after_tax_comparison,
    ownership_tax_comparisons,
    tax_advisor_insights,
)
from engine.simulation import project_annually


def _configuration() -> WealthOsConfig:
    return load_configuration(Path("data/example_household.yaml").read_text(encoding="utf-8"))


def test_gross_to_net_statement_reconciles_without_raw_decimal_precision() -> None:
    """The first retirement reporting bridge uses the completed Task 3B values unchanged."""
    configuration = _configuration()
    projection = project_annually(configuration)
    statement = annual_tax_statement(projection, configuration, 2032)

    assert statement.enabled is True
    assert statement.gross_recurring_income - statement.total_tax == statement.net_recurring_income
    assert statement.total_funding == statement.retirement_spending
    assert statement.people[0].result.standard_rate_income >= Decimal("0")
    assert format_eur_cents(statement.total_tax).count(".") == 1
    assert len(format_eur_cents(statement.total_tax).split(".")[1]) == 2


def test_tax_disabled_statement_is_a_status_not_calculated_zero_tax() -> None:
    """Legacy no-tax configurations remain explicit about their gross-income treatment."""
    configuration = _configuration().model_copy(
        update={"tax": _configuration().tax.model_copy(update={"enabled": False})}
    )
    projection = project_annually(configuration)
    statement = annual_tax_statement(projection, configuration, 2032)

    assert statement.enabled is False
    assert statement.people == ()
    assert statement.net_recurring_income == statement.gross_recurring_income


def test_before_after_and_ownership_comparisons_are_immutable_and_deterministic() -> None:
    """Presentation scenarios retain the saved ownership split and compare all five cases."""
    configuration = _configuration()
    saved_owners = configuration.rental_properties[0].owners
    comparison = before_after_tax_comparison(configuration)
    ownership = ownership_tax_comparisons(configuration, "Ardfield Court")

    assert comparison is not None
    assert comparison.liquid_funding_after_tax > comparison.liquid_funding_before_tax
    assert len(ownership) == 5
    assert configuration.rental_properties[0].owners == saved_owners
    assert ownership == ownership_tax_comparisons(configuration, "Ardfield Court")
    assert max(item.total_tax for item in ownership) > min(item.total_tax for item in ownership)


def test_tax_advisor_insights_are_evidence_based_and_qualified() -> None:
    """Advisor prose reports modelled effects and the material CGT limitation."""
    insights = tax_advisor_insights(_configuration())
    assert any("liquid funding" in insight for insight in insights)
    assert any("CGT" in insight for insight in insights)
    assert all("optimal" not in insight.lower() for insight in insights)
