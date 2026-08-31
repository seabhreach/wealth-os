"""Reporting application boundary."""

from engine.reporting.advisor import (
    AdvisorScenario,
    ScenarioMetrics,
    ScenarioOverride,
    ScenarioResult,
    SensitivityResult,
    advisor_insights,
    apply_override,
    default_scenarios,
    retirement_age_explorer,
    run_default_scenarios,
    run_scenario,
    sensitivity_analysis,
)
from engine.reporting.comparison import (
    RetirementComparison,
    RetirementComparisonMetric,
    compare_retirement_readiness,
)
from engine.reporting.explainability import (
    AnnualCalculationTrace,
    annual_calculation_trace,
    preserved_wealth_warning,
    retirement_funding_explanation,
)
from engine.reporting.properties import RentalPropertySummary, summarize_rental_properties
from engine.reporting.property_reconciliation import (
    PropertyScenarioReconciliation,
    reconcile_property_scenarios,
)
from engine.reporting.retirement import RetirementReadinessSummary, summarize_retirement_readiness
from engine.reporting.rsu_audit import (
    AmazonShareBridgeRow,
    CashBridgeRow,
    RsuAuditSummary,
    summarize_rsu_audit,
)
from engine.reporting.statements import (
    AnnualFinancialStatement,
    AnnualFundingStatement,
    AssetMovementStatement,
    annual_financial_statement,
    retirement_funding_narrative,
)
from engine.reporting.tax import (
    AnnualTaxStatement,
    BeforeAfterTaxComparison,
    PersonTaxStatement,
    TaxOwnershipComparison,
    annual_tax_statement,
    before_after_tax_comparison,
    ownership_tax_comparisons,
    tax_advisor_insights,
    tax_over_time,
)

__all__ = [
    "AdvisorScenario",
    "AmazonShareBridgeRow",
    "AnnualCalculationTrace",
    "AnnualFinancialStatement",
    "AnnualFundingStatement",
    "AnnualTaxStatement",
    "AssetMovementStatement",
    "BeforeAfterTaxComparison",
    "CashBridgeRow",
    "PersonTaxStatement",
    "PropertyScenarioReconciliation",
    "RentalPropertySummary",
    "RetirementComparison",
    "RetirementComparisonMetric",
    "RetirementReadinessSummary",
    "RsuAuditSummary",
    "ScenarioMetrics",
    "ScenarioOverride",
    "ScenarioResult",
    "SensitivityResult",
    "TaxOwnershipComparison",
    "advisor_insights",
    "annual_calculation_trace",
    "annual_financial_statement",
    "annual_tax_statement",
    "apply_override",
    "before_after_tax_comparison",
    "compare_retirement_readiness",
    "default_scenarios",
    "ownership_tax_comparisons",
    "preserved_wealth_warning",
    "reconcile_property_scenarios",
    "retirement_age_explorer",
    "retirement_funding_explanation",
    "retirement_funding_narrative",
    "run_default_scenarios",
    "run_scenario",
    "sensitivity_analysis",
    "summarize_rental_properties",
    "summarize_retirement_readiness",
    "summarize_rsu_audit",
    "tax_advisor_insights",
    "tax_over_time",
]
