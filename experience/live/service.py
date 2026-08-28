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
from experience.live.scenario_actions import (
    g001_scenario_override,
    supported_g001_retirement_ages,
)
from experience.models import EvidencePurpose, GoalId, InformationStatus
from experience.workspace_composition.models import SetScenarioValue

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

    @property
    def supported_retirement_ages(self) -> tuple[int, ...]:
        """Return the bounded G-001 retirement-age control values."""

        return supported_g001_retirement_ages(self._baseline.configuration)

    def retire_earlier(self, retirement_age: int = 58) -> LiveWorkspace:
        """Compare baseline with one validated temporary retirement-age override."""

        config = self._baseline.configuration
        action = SetScenarioValue("retirement_age", retirement_age)
        override = g001_scenario_override(config, action)
        scenario = run_scenario(
            config,
            AdvisorScenario(
                f"Retire at {retirement_age}",
                override,
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
                ("g001-age", "g001-funding-status"),
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
                "g001-funding-status",
                "Funding horizon",
                EvidencePurpose.COMPARISON,
                LIVE,
                "Modelled funding outcome",
                "Baseline",
                _funding_status(baseline),
                "Explored",
                _funding_status(scenario),
                "",
            ),
            ComparisonEvidence(
                "g001-liquid-final",
                "Final liquid assets",
                EvidencePurpose.COMPARISON,
                LIVE,
                "Liquid assets at life expectancy",
                "Baseline",
                baseline.metrics.liquid_assets_at_life_expectancy,
                "Explored",
                scenario.metrics.liquid_assets_at_life_expectancy,
                "EUR",
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
                "g001-liquid-baseline-series",
                "Baseline liquid assets",
                EvidencePurpose.COMPARISON,
                LIVE,
                f"Baseline · retire at {baseline.metrics.retirement_age}",
                "EUR",
                _projection_liquid_points(baseline),
            ),
            TimelineEvidence(
                "g001-liquid-scenario-series",
                "Explored liquid assets",
                EvidencePurpose.COMPARISON,
                LIVE,
                f"Explored · retire at {scenario.metrics.retirement_age}",
                "EUR",
                _projection_liquid_points(scenario),
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
            *_retirement_milestone_evidence(baseline, scenario),
            *_retirement_tradeoff_evidence(baseline, scenario),
            NarrativeEvidence(
                "g001-explanation",
                "Why?",
                EvidencePurpose.EXPLANATION,
                LIVE,
                _retirement_explanation(scenario),
                (
                    "g001-liquid-scenario-series",
                    "g001-milestone-explored-retirement",
                    "g001-milestone-private-pension",
                    "g001-milestone-state-pension",
                ),
            ),
            TableEvidence(
                "g001-bridge",
                "Funding bridge",
                EvidencePurpose.EXPLANATION,
                LIVE,
                ("Period", "Modelled value"),
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
                "Temporary scenario input",
                KNOWN,
            ),
            AssumptionEvidence(
                "g001-spending-assumption",
                "Retirement spending",
                EvidencePurpose.ASSUMPTION,
                LIVE,
                "Annual retirement spending",
                config.assumptions.target_retirement_income,
                "Validated baseline assumption",
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
                "This illustration retains the existing v0.2 return, tax, pension-access, inflation and longevity assumptions.",
            ),
        )
        return self._workspace(
            GoalId.RETIRE_EARLIER,
            f"Could I retire at {retirement_age}?",
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
                "Configured inputs from the existing property record.",
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
                "Existing v0.2 comparison metric",
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
                "The metric is the existing v0.2 exposure ratio; the Experience does not define a new investable-assets concentration formula. Disposal taxes are not modelled.",
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
                    "No temporary multi-year result is shown because the v0.2 model has no supported override for that schedule.",
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
                _cash_decline_answer(statement),
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
                    ("ETF units sold", statement.funding.etf_units_sold),
                    ("Employer-equity shares sold", statement.funding.amazon_shares_sold),
                    ("Unfunded amount", statement.funding.unfunded_amount),
                ),
                "Categories are copied from the existing annual statement and calculation trace.",
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
                "No new Financial Picture data was requested. The explanation is limited to categories exposed by existing v0.2 reporting and trace evidence.",
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


def _projection_liquid_points(result: ScenarioResult) -> tuple[TimelinePoint, ...]:
    """Expose exact annual liquid-assets evidence without interpolation."""

    return tuple(
        TimelinePoint(year.calendar_year, year.liquid_assets, year.age)
        for year in result.projection
    )


def _selected_liquid_points(result: ScenarioResult) -> tuple[TimelinePoint, ...]:
    first = result.projection[0]
    retirement = next(year for year in result.projection if not year.employed)
    final = result.projection[-1]
    return tuple(
        TimelinePoint(year.calendar_year, year.liquid_assets, year.age)
        for year in (first, retirement, final)
    )


def _retirement_answer(result: ScenarioResult) -> str:
    if result.metrics.retirement_ready:
        return (
            f"Yes — under the current assumptions, retiring at {result.metrics.retirement_age} "
            "remains funded through the planning horizon."
        )
    return (
        f"Under the current assumptions, retiring at {result.metrics.retirement_age} "
        f"first becomes unfunded in {result.metrics.first_unfunded_year}."
    )


def _funding_status(result: ScenarioResult) -> str:
    """Translate the existing readiness result without adding a new metric."""

    if result.metrics.retirement_ready:
        return "Funded through planning horizon"
    return f"First unfunded in {result.metrics.first_unfunded_year}"


def _retirement_milestone_evidence(
    baseline: ScenarioResult,
    scenario: ScenarioResult,
) -> tuple[MetricEvidence, ...]:
    """Reference milestones already present in completed scenario projections."""

    baseline_retirement = next(year for year in baseline.projection if not year.employed)
    explored_retirement = next(year for year in scenario.projection if not year.employed)
    private_pension = next(
        (year for year in scenario.projection if year.private_pension_income > 0),
        None,
    )
    state_pension = next(
        (year for year in scenario.projection if year.state_pension_income > 0),
        None,
    )
    evidence = [
        MetricEvidence(
            "g001-milestone-explored-retirement",
            "Explored retirement",
            EvidencePurpose.EXPLANATION,
            LIVE,
            "Stop employment",
            explored_retirement.calendar_year,
            "calendar year",
            f"Age {explored_retirement.age}",
        ),
        MetricEvidence(
            "g001-milestone-baseline-retirement",
            "Baseline retirement",
            EvidencePurpose.EXPLANATION,
            LIVE,
            "Current plan",
            baseline_retirement.calendar_year,
            "calendar year",
            f"Age {baseline_retirement.age}",
        ),
    ]
    if private_pension is not None:
        evidence.append(
            MetricEvidence(
                "g001-milestone-private-pension",
                "Private pension begins",
                EvidencePurpose.EXPLANATION,
                LIVE,
                "First modelled private-pension income",
                private_pension.calendar_year,
                "calendar year",
                f"Age {private_pension.age}",
            )
        )
    if state_pension is not None:
        evidence.append(
            MetricEvidence(
                "g001-milestone-state-pension",
                "State Pension begins",
                EvidencePurpose.EXPLANATION,
                LIVE,
                "First modelled State Pension income",
                state_pension.calendar_year,
                "calendar year",
                f"Age {state_pension.age}",
            )
        )
    return tuple(evidence)


def _retirement_tradeoff_evidence(
    baseline: ScenarioResult,
    scenario: ScenarioResult,
) -> tuple[InsightEvidence, ...]:
    """Describe bounded comparisons already present in scenario results."""

    if scenario.metrics.retirement_age < baseline.metrics.retirement_age:
        time_observation = (
            f"Employment stops at age {scenario.metrics.retirement_age} instead of the baseline "
            f"age {baseline.metrics.retirement_age}."
        )
    elif scenario.metrics.retirement_age > baseline.metrics.retirement_age:
        time_observation = (
            f"Employment continues until age {scenario.metrics.retirement_age} instead of the "
            f"baseline age {baseline.metrics.retirement_age}."
        )
    else:
        time_observation = "The explored retirement age matches the baseline plan."

    if scenario.metrics.final_net_worth < baseline.metrics.final_net_worth:
        financial_observation = "Final modelled net worth is lower than the baseline path."
    elif scenario.metrics.final_net_worth > baseline.metrics.final_net_worth:
        financial_observation = "Final modelled net worth is higher than the baseline path."
    else:
        financial_observation = "Final modelled net worth matches the baseline path."

    return (
        InsightEvidence(
            "g001-tradeoff-time",
            "Time",
            EvidencePurpose.TRADE_OFF,
            LIVE,
            time_observation,
            ("g001-age",),
        ),
        InsightEvidence(
            "g001-tradeoff-financial",
            "Financial effect",
            EvidencePurpose.TRADE_OFF,
            LIVE,
            financial_observation,
            ("g001-net-worth", "g001-liquid-final"),
        ),
        InsightEvidence(
            "g001-tradeoff-constant",
            "Held constant",
            EvidencePurpose.TRADE_OFF,
            LIVE,
            "The annual retirement-spending assumption is unchanged in this comparison.",
            ("g001-spending-assumption",),
        ),
    )


def _retirement_explanation(result: ScenarioResult) -> str:
    """Explain the bridge using only milestones and funding evidence in the projection."""

    retirement = next(year for year in result.projection if not year.employed)
    private_pension = next(
        (year for year in result.projection if year.private_pension_income > 0),
        None,
    )
    state_pension = next(
        (year for year in result.projection if year.state_pension_income > 0),
        None,
    )
    sentences = [f"Employment income stops at age {retirement.age} in {retirement.calendar_year}."]
    if private_pension is not None and private_pension.calendar_year > retirement.calendar_year:
        sentences.append(
            "Liquid assets help fund spending until private-pension income first appears in "
            f"{private_pension.calendar_year}."
        )
    elif private_pension is not None:
        sentences.append(
            f"Private-pension income first appears in {private_pension.calendar_year}."
        )
    if state_pension is not None:
        sentences.append(f"State Pension income first appears in {state_pension.calendar_year}.")
    return " ".join(sentences)


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


def _cash_decline_answer(statement: AnnualFinancialStatement) -> str:
    funding = statement.funding
    recurring_sources: list[str] = []
    if funding.rental_income > 0:
        recurring_sources.append("rental income")
    if funding.private_pension_income > 0:
        recurring_sources.append("private-pension income")
    if funding.state_pension > 0:
        recurring_sources.append("State Pension income")

    if recurring_sources and funding.cash_used > 0:
        sources = _join_sources(recurring_sources)
        cause = f"{sources.capitalize()} cover part of retirement spending; the remainder comes from cash."
    elif recurring_sources:
        sources = _join_sources(recurring_sources)
        cause = f"{sources.capitalize()} cover retirement spending without a cash withdrawal."
    elif funding.cash_used > 0:
        cause = "Cash covers the retirement-spending need in the selected year."
    else:
        cause = "No cash withdrawal is required for retirement spending in the selected year."
    return (
        f"In {statement.calendar_year}, {cause} The annual trace links opening cash, "
        "income, purchases and cash used for spending to closing cash."
    )


def _join_sources(sources: list[str]) -> str:
    if len(sources) == 1:
        return sources[0]
    return f"{', '.join(sources[:-1])} and {sources[-1]}"


def _property_picture_keys(baseline: LiveBaseline) -> tuple[str, ...]:
    keys = ["cash", "planned_retirement_age"]
    for property_config in baseline.configuration.rental_properties:
        prefix = f"property:{property_config.name}"
        keys.extend((f"{prefix}:year", f"{prefix}:price", f"{prefix}:rent"))
    return tuple(keys)
