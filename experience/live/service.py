# ruff: noqa: E501
"""Application service adapting existing v0.2 outputs into live evidence."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from engine.reporting import (
    AdvisorScenario,
    AnnualFinancialStatement,
    ScenarioOverride,
    ScenarioResult,
    annual_financial_statement,
    retirement_funding_narrative,
    run_scenario,
    summarize_rental_properties,
)
from experience.live.financial_picture import BASELINE_IDENTIFIER, LiveBaseline, load_live_baseline
from experience.live.models import (
    AssumptionEvidence,
    ComparisonEvidence,
    EvidenceMode,
    FinancialStatementEvidence,
    InsightEvidence,
    LimitationEvidence,
    LiveEvidence,
    LiveWorkspace,
    MetricEvidence,
    NarrativeEvidence,
    StrategyEvidence,
    TableEvidence,
    TimelineEvidence,
    TimelinePoint,
)
from experience.live.provenance import build_provenance, tax_rule_identifier
from experience.models import EvidencePurpose, GoalId, InformationStatus

LIVE = EvidenceMode.LIVE
KNOWN = InformationStatus.KNOWN


class LiveExperienceService:
    """Read-only orchestration over validated v0.2 reporting and simulation APIs."""

    def __init__(self, baseline: LiveBaseline) -> None:
        self._baseline = baseline
        self._baseline_result = run_scenario(
            baseline.configuration,
            AdvisorScenario("Baseline", ScenarioOverride()),
        )
        self._tax_identifier = tax_rule_identifier(baseline.configuration, baseline.repository_root)

    @classmethod
    def from_example(cls, repository_root: Path) -> LiveExperienceService:
        """Load the repository's declared v0.2 example configuration."""

        return cls(load_live_baseline(repository_root / "data" / "example_household.yaml"))

    @property
    def baseline(self) -> LiveBaseline:
        """Expose the immutable adapter result for audit and tests."""

        return self._baseline

    @property
    def supported_years(self) -> tuple[int, ...]:
        """Return reporting years already produced by the baseline engine run."""

        return tuple(year.calendar_year for year in self._baseline_result.projection)

    def retire_earlier(self, retirement_age: int = 58) -> LiveWorkspace:
        """Compare baseline with one validated temporary retirement-age override."""

        config = self._baseline.configuration
        if not config.household.current_age <= retirement_age <= config.household.life_expectancy:
            raise ValueError("Retirement age must be within the validated projection horizon.")
        scenario = run_scenario(
            config,
            AdvisorScenario(
                f"Retire at {retirement_age}",
                ScenarioOverride(retirement_age=retirement_age),
            ),
        )
        baseline = self._baseline_result
        first_retirement = next(year for year in scenario.projection if not year.employed)
        final_year = scenario.projection[-1]
        overrides = (("retirement_age", str(retirement_age)),)
        evidence: tuple[LiveEvidence, ...] = (
            NarrativeEvidence(
                "g001-answer",
                "Answer",
                EvidencePurpose.ANSWER,
                LIVE,
                _retirement_answer(scenario),
                ("g001-age", "g001-net-worth"),
            ),
            ComparisonEvidence(
                "g001-age",
                "Retirement timing",
                EvidencePurpose.COMPARISON,
                LIVE,
                "Retirement age",
                "Baseline",
                baseline.metrics.retirement_age,
                "Explored",
                scenario.metrics.retirement_age,
                "years old",
            ),
            ComparisonEvidence(
                "g001-net-worth",
                "Final modelled net worth",
                EvidencePurpose.COMPARISON,
                LIVE,
                "Net worth at life expectancy",
                "Baseline",
                baseline.metrics.final_net_worth,
                "Explored",
                scenario.metrics.final_net_worth,
                "EUR",
            ),
            TimelineEvidence(
                "g001-liquid-timeline",
                "Liquid-assets trajectory",
                EvidencePurpose.EXPLANATION,
                LIVE,
                "Liquid assets",
                "EUR",
                _selected_liquid_points(scenario),
            ),
            TableEvidence(
                "g001-bridge",
                "Funding bridge",
                EvidencePurpose.EXPLANATION,
                LIVE,
                ("Period", "Engine output"),
                (
                    ("First retirement year", first_retirement.calendar_year),
                    ("Liquid assets", first_retirement.liquid_assets),
                    ("Private pension income", first_retirement.private_pension_income),
                    ("Liquid funding", first_retirement.withdrawal_amount),
                    ("Final liquid assets", final_year.liquid_assets),
                ),
                "Values come directly from the completed scenario projection.",
            ),
            AssumptionEvidence(
                "g001-assumption",
                "Temporary assumption",
                EvidencePurpose.ASSUMPTION,
                LIVE,
                "Retirement age",
                retirement_age,
                "Validated ScenarioOverride",
                KNOWN,
            ),
            StrategyEvidence(
                "g001-strategy",
                "Proposed update",
                EvidencePurpose.STRATEGY,
                LIVE,
                f"Retire at {baseline.metrics.retirement_age}",
                f"Retire at {scenario.metrics.retirement_age}",
                overrides,
                "Preview only — the baseline retirement age has not been changed.",
            ),
            LimitationEvidence(
                "g001-limitation",
                "Limitations",
                EvidencePurpose.LIMITATION,
                LIVE,
                "This deterministic illustration retains the existing v0.2 return, tax, pension-access, inflation and longevity assumptions.",
            ),
        )
        return self._workspace(
            GoalId.RETIRE_EARLIER,
            "Retire Earlier — Live",
            evidence,
            overrides,
            (baseline, scenario),
            (
                "current_age",
                "partner_age",
                "planned_retirement_age",
                "retirement_spending",
                "cash",
                "investments",
            ),
            proposed_update="Retirement age change preview — not persisted",
        )

    def property_decision(self, *, financing: bool = False) -> LiveWorkspace:
        """Compare configured property inclusion or expose unsupported financing."""

        baseline = self._baseline_result
        if financing:
            overrides = (("financing", "requested"),)
            evidence: tuple[LiveEvidence, ...] = (
                NarrativeEvidence(
                    "g002-answer",
                    "Answer",
                    EvidencePurpose.ANSWER,
                    LIVE,
                    "The existing v0.2 model cannot produce a financed-property comparison.",
                    ("g002-financing-limit",),
                ),
                LimitationEvidence(
                    "g002-financing-limit",
                    "Financing is unsupported",
                    EvidencePurpose.LIMITATION,
                    LIVE,
                    "Mortgage balances, interest, repayments and financing cash flows are not modelled. No result has been inferred.",
                ),
            )
            return self._workspace(
                GoalId.INVESTMENT_PROPERTY,
                "Investment Property — Live",
                evidence,
                overrides,
                baseline,
                _property_picture_keys(self._baseline),
            )

        excluded = run_scenario(
            self._baseline.configuration,
            AdvisorScenario(
                "Exclude planned property",
                ScenarioOverride(include_planned_rental_properties=False),
            ),
        )
        properties = summarize_rental_properties(self._baseline.configuration)
        overrides = (("include_planned_rental_properties", "false"),)
        property_rows = tuple(
            (
                item.name,
                item.purchase_year,
                item.purchase_price,
                item.annual_net_rent,
            )
            for item in properties
        )
        evidence = (
            NarrativeEvidence(
                "g002-answer",
                "Answer",
                EvidencePurpose.ANSWER,
                LIVE,
                "The live comparison shows the configured planned property beside an otherwise identical projection with that planned purchase excluded.",
                ("g002-liquidity", "g002-property-value"),
            ),
            ComparisonEvidence(
                "g002-liquidity",
                "Final liquid assets",
                EvidencePurpose.TRADE_OFF,
                LIVE,
                "Liquid assets at life expectancy",
                "Property included",
                baseline.metrics.liquid_assets_at_life_expectancy,
                "Property excluded",
                excluded.metrics.liquid_assets_at_life_expectancy,
                "EUR",
            ),
            ComparisonEvidence(
                "g002-property-value",
                "Final property value",
                EvidencePurpose.COMPARISON,
                LIVE,
                "Property value at life expectancy",
                "Property included",
                baseline.metrics.final_property_value,
                "Property excluded",
                excluded.metrics.final_property_value,
                "EUR",
            ),
            ComparisonEvidence(
                "g002-rent",
                "First-retirement rental income",
                EvidencePurpose.EXPLANATION,
                LIVE,
                "Rental income",
                "Property included",
                baseline.metrics.first_retirement_rental_income,
                "Property excluded",
                excluded.metrics.first_retirement_rental_income,
                "EUR/year",
            ),
            TableEvidence(
                "g002-configured-property",
                "Configured property",
                EvidencePurpose.ASSUMPTION,
                LIVE,
                ("Property", "Purchase year", "Purchase price", "Annual net rent"),
                property_rows,
                "Configured inputs reported by the existing property-reporting API.",
            ),
            StrategyEvidence(
                "g002-strategy",
                "Proposed update",
                EvidencePurpose.STRATEGY,
                LIVE,
                "Configured planned property included",
                "Planned property excluded",
                overrides,
                "Preview only — the configured property remains in the baseline.",
            ),
            LimitationEvidence(
                "g002-limitation",
                "Limitations",
                EvidencePurpose.LIMITATION,
                LIVE,
                "Mortgages, transaction costs, vacancy, detailed maintenance and unmodelled tax effects are excluded.",
            ),
        )
        return self._workspace(
            GoalId.INVESTMENT_PROPERTY,
            "Investment Property — Live",
            evidence,
            overrides,
            (baseline, excluded),
            _property_picture_keys(self._baseline),
            proposed_update="Property inclusion change preview — not persisted",
        )

    def employer_equity(self, *, focus_sell_on_vest: bool = False) -> LiveWorkspace:
        """Compare the two disposal policies already supported by v0.2."""

        config = self._baseline.configuration
        sell = run_scenario(
            config,
            AdvisorScenario("Sell on vest", ScenarioOverride(sell_on_vest=True)),
        )
        retain = run_scenario(
            config,
            AdvisorScenario("Retain", ScenarioOverride(sell_on_vest=False)),
        )
        focus = "sell on vest" if focus_sell_on_vest else "retain"
        overrides = (("sell_on_vest", str(focus_sell_on_vest).lower()),)
        evidence: tuple[LiveEvidence, ...] = (
            NarrativeEvidence(
                "g003-answer",
                "Answer",
                EvidencePurpose.ANSWER,
                LIVE,
                f"The live Workspace compares supported sell-on-vest and retain policies and currently focuses on {focus}.",
                ("g003-concentration", "g003-final-worth"),
            ),
            ComparisonEvidence(
                "g003-concentration",
                "Maximum employer-equity concentration",
                EvidencePurpose.TRADE_OFF,
                LIVE,
                "Maximum concentration",
                "Sell on vest",
                sell.metrics.maximum_amazon_concentration,
                "Retain",
                retain.metrics.maximum_amazon_concentration,
                "ratio",
            ),
            ComparisonEvidence(
                "g003-final-equity",
                "Final employer-equity value",
                EvidencePurpose.COMPARISON,
                LIVE,
                "Employer-equity value at life expectancy",
                "Sell on vest",
                sell.metrics.final_amazon_value,
                "Retain",
                retain.metrics.final_amazon_value,
                "EUR",
            ),
            ComparisonEvidence(
                "g003-final-worth",
                "Final net worth",
                EvidencePurpose.COMPARISON,
                LIVE,
                "Net worth at life expectancy",
                "Sell on vest",
                sell.metrics.final_net_worth,
                "Retain",
                retain.metrics.final_net_worth,
                "EUR",
            ),
            AssumptionEvidence(
                "g003-denominator",
                "Concentration definition",
                EvidencePurpose.ASSUMPTION,
                LIVE,
                "Denominator",
                "Existing v0.2 net-worth denominator",
                "Existing v0.2 scenario metric",
                KNOWN,
            ),
            StrategyEvidence(
                "g003-strategy",
                "Proposed update",
                EvidencePurpose.STRATEGY,
                LIVE,
                "Configured sell-on-vest policy",
                f"Focus on {focus}",
                overrides,
                "Preview only — the employer-equity policy has not been persisted.",
            ),
            LimitationEvidence(
                "g003-limitation",
                "Limitations",
                EvidencePurpose.LIMITATION,
                LIVE,
                "The metric is the existing engine exposure ratio; the Experience does not define a new investable-assets concentration formula. Disposal taxes are not modelled.",
            ),
        )
        return self._workspace(
            GoalId.EMPLOYER_EQUITY,
            "Employer Equity Exposure — Live",
            evidence,
            overrides,
            (sell, retain),
            ("employer_equity", "equity_policy", "cash", "investments"),
            proposed_update="Employer-equity policy preview — not persisted",
        )

    def higher_spending(
        self,
        target: Decimal = Decimal("100000"),
        *,
        temporary_years: int | None = None,
    ) -> LiveWorkspace:
        """Run a permanent spending override or expose the unsupported temporary case."""

        if target < Decimal("0"):
            raise ValueError("Retirement spending must not be negative.")
        baseline = self._baseline_result
        if temporary_years is not None:
            overrides: tuple[tuple[str, str], ...] = (
                ("target_retirement_spending", format(target, "f")),
                ("temporary_years", str(temporary_years)),
            )
            evidence: tuple[LiveEvidence, ...] = (
                NarrativeEvidence(
                    "g004-answer",
                    "Answer",
                    EvidencePurpose.ANSWER,
                    LIVE,
                    "The existing v0.2 override supports a permanent spending change, not a temporary multi-year schedule.",
                    ("g004-temporary-limit",),
                ),
                LimitationEvidence(
                    "g004-temporary-limit",
                    "Temporary spending is unsupported",
                    EvidencePurpose.LIMITATION,
                    LIVE,
                    "No temporary multi-year result is shown because the engine has no supported override for that schedule.",
                ),
            )
            return self._workspace(
                GoalId.HIGHER_SPENDING,
                "Higher Retirement Spending — Live",
                evidence,
                overrides,
                baseline,
                ("retirement_spending", "inflation", "cash", "investments"),
            )

        scenario = run_scenario(
            self._baseline.configuration,
            AdvisorScenario(
                "Higher permanent spending",
                ScenarioOverride(target_retirement_spending=target),
            ),
        )
        overrides = (("target_retirement_spending", format(target, "f")),)
        evidence = (
            NarrativeEvidence(
                "g004-answer",
                "Answer",
                EvidencePurpose.ANSWER,
                LIVE,
                _spending_answer(scenario),
                ("g004-spending", "g004-liquid"),
            ),
            ComparisonEvidence(
                "g004-spending",
                "Retirement spending",
                EvidencePurpose.COMPARISON,
                LIVE,
                "First-retirement spending",
                "Baseline",
                baseline.metrics.first_retirement_spending,
                "Permanent higher spending",
                scenario.metrics.first_retirement_spending,
                "EUR/year",
            ),
            ComparisonEvidence(
                "g004-liquid",
                "Final liquid assets",
                EvidencePurpose.TRADE_OFF,
                LIVE,
                "Liquid assets at life expectancy",
                "Baseline",
                baseline.metrics.liquid_assets_at_life_expectancy,
                "Permanent higher spending",
                scenario.metrics.liquid_assets_at_life_expectancy,
                "EUR",
            ),
            ComparisonEvidence(
                "g004-final-worth",
                "Final net worth",
                EvidencePurpose.COMPARISON,
                LIVE,
                "Net worth at life expectancy",
                "Baseline",
                baseline.metrics.final_net_worth,
                "Permanent higher spending",
                scenario.metrics.final_net_worth,
                "EUR",
            ),
            MetricEvidence(
                "g004-unfunded",
                "First unfunded year",
                EvidencePurpose.INSIGHT,
                LIVE,
                "First unfunded year",
                scenario.metrics.first_unfunded_year or "None",
                "calendar year",
            ),
            StrategyEvidence(
                "g004-strategy",
                "Proposed update",
                EvidencePurpose.STRATEGY,
                LIVE,
                f"Permanent spending {baseline.metrics.first_retirement_spending} EUR/year",
                f"Permanent spending {scenario.metrics.first_retirement_spending} EUR/year",
                overrides,
                "Preview only — baseline spending has not been changed.",
            ),
            LimitationEvidence(
                "g004-limitation",
                "Limitations",
                EvidencePurpose.LIMITATION,
                LIVE,
                "Only a permanent net-spending override is supported. Existing inflation, tax and longevity semantics are unchanged.",
            ),
        )
        return self._workspace(
            GoalId.HIGHER_SPENDING,
            "Higher Retirement Spending — Live",
            evidence,
            overrides,
            (baseline, scenario),
            ("retirement_spending", "inflation", "cash", "investments"),
            proposed_update="Permanent retirement-spending preview — not persisted",
        )

    def cash_decline(self, calendar_year: int = 2032) -> LiveWorkspace:
        """Explain one reporting year solely through existing statement and trace APIs."""

        projection = self._baseline_result.projection
        statement = annual_financial_statement(
            projection, self._baseline.configuration, calendar_year
        )
        trace = statement.assets.trace
        overrides = (("calendar_year", str(calendar_year)),)
        evidence: tuple[LiveEvidence, ...] = (
            NarrativeEvidence(
                "g005-answer",
                "Answer",
                EvidencePurpose.ANSWER,
                LIVE,
                (
                    f"{retirement_funding_narrative(statement)} "
                    "The annual trace links opening cash, configured inflows, purchases and cash used for spending to closing cash."
                ),
                ("g005-statement", "g005-funding"),
            ),
            FinancialStatementEvidence(
                "g005-statement",
                f"Cash movement in {calendar_year}",
                EvidencePurpose.EXPLANATION,
                LIVE,
                calendar_year,
                trace.opening_cash,
                (
                    ("Annual savings", trace.annual_savings),
                    ("Employer-equity sale proceeds", trace.rsu_sale_proceeds),
                    ("Rental income", trace.rental_income),
                    ("Private pension income", trace.private_pension_income),
                    ("State Pension income", trace.state_pension_income),
                ),
                (
                    ("Estimated tax", trace.total_estimated_tax),
                    ("Property purchase", trace.property_purchase_cost),
                    ("Retirement spending", trace.retirement_spending),
                    ("Cash used for spending", trace.cash_withdrawal),
                ),
                trace.closing_cash,
                statement.liquid_assets,
                statement.net_worth,
            ),
            TableEvidence(
                "g005-funding",
                "Funding sources",
                EvidencePurpose.EXPLANATION,
                LIVE,
                ("Category", "Existing reporting value"),
                (
                    ("Rental income", statement.funding.rental_income),
                    ("Private pension income", statement.funding.private_pension_income),
                    ("State Pension", statement.funding.state_pension),
                    ("Estimated income tax", statement.funding.estimated_income_tax),
                    ("Estimated USC", statement.funding.estimated_usc),
                    ("Cash used", statement.funding.cash_used),
                    ("ETF sales", statement.funding.etf_units_sold),
                    ("Employer-equity sales", statement.funding.amazon_shares_sold),
                    ("Unfunded amount", statement.funding.unfunded_amount),
                ),
                "Categories are copied from AnnualFinancialStatement and AnnualCalculationTrace.",
            ),
            InsightEvidence(
                "g005-transition",
                "Asset transition",
                EvidencePurpose.INSIGHT,
                LIVE,
                _cash_transition_observation(statement),
                ("g005-statement", "g005-funding"),
            ),
            LimitationEvidence(
                "g005-limitation",
                "Evidence boundary",
                EvidencePurpose.LIMITATION,
                LIVE,
                "No new Financial Picture data was requested. The explanation is limited to categories exposed by existing v0.2 reporting and trace APIs.",
            ),
        )
        return self._workspace(
            GoalId.CASH_DECLINE,
            "Cash Decline Explanation — Live",
            evidence,
            overrides,
            statement,
            ("cash", "retirement_spending", "tax", "planned_retirement_age"),
        )

    def _workspace(
        self,
        goal_id: GoalId,
        title: str,
        evidence: tuple[LiveEvidence, ...],
        overrides: tuple[tuple[str, str], ...],
        deterministic_result: object,
        picture_item_keys: tuple[str, ...],
        proposed_update: str | None = None,
    ) -> LiveWorkspace:
        picture = self._baseline.financial_picture
        provenance = build_provenance(
            baseline_identifier=BASELINE_IDENTIFIER,
            picture_fingerprint=picture.fingerprint,
            goal_id=goal_id,
            scenario_overrides=overrides,
            tax_identifier=self._tax_identifier,
            deterministic_result=deterministic_result,
        )
        return LiveWorkspace(
            workspace_id=f"live-{goal_id.value}-{provenance.result_fingerprint[:12]}",
            goal_id=goal_id,
            title=title,
            mode=LIVE,
            evidence=evidence,
            financial_picture=picture,
            picture_item_keys=picture_item_keys,
            provenance=provenance,
            proposed_update=proposed_update,
        )


def _selected_liquid_points(result: ScenarioResult) -> tuple[TimelinePoint, ...]:
    first = result.projection[0]
    retirement = next(year for year in result.projection if not year.employed)
    final = result.projection[-1]
    return tuple(
        TimelinePoint(year.calendar_year, year.liquid_assets) for year in (first, retirement, final)
    )


def _retirement_answer(result: ScenarioResult) -> str:
    if result.metrics.retirement_ready:
        return (
            f"Under the existing v0.2 assumptions, retiring at {result.metrics.retirement_age} "
            "remains fully funded through the configured life expectancy."
        )
    return (
        f"Under the existing v0.2 assumptions, retiring at {result.metrics.retirement_age} "
        f"first becomes unfunded in {result.metrics.first_unfunded_year}."
    )


def _spending_answer(result: ScenarioResult) -> str:
    if result.metrics.retirement_ready:
        return "The permanent higher-spending scenario remains funded under the existing v0.2 assumptions."
    return f"The permanent higher-spending scenario first becomes unfunded in {result.metrics.first_unfunded_year}."


def _cash_transition_observation(statement: AnnualFinancialStatement) -> str:
    funding = statement.funding
    if funding.etf_units_sold:
        return "The selected year has moved beyond cash-only funding and includes ETF sales."
    if funding.amazon_shares_sold:
        return "The selected year includes employer-equity sales after earlier liquid sources."
    if funding.cash_used:
        return "Cash is the liquid source used for the remaining spending gap in the selected year."
    return "No liquid-asset sale is required in the selected year."


def _property_picture_keys(baseline: LiveBaseline) -> tuple[str, ...]:
    keys = ["cash", "planned_retirement_age"]
    for property_config in baseline.configuration.rental_properties:
        prefix = f"property:{property_config.name}"
        keys.extend((f"{prefix}:year", f"{prefix}:price", f"{prefix}:rent"))
    return tuple(keys)
