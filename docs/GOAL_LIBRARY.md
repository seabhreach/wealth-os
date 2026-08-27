# Goal Library

## Purpose

This library defines five validated experience goals. A goal describes the question Wealth OS
helps a person explore; it is not a recommendation or a claim that the model can choose for them.
Information requirements are governed by the [Discovery Model](RFC-012_DISCOVERY_MODEL.md).

## G-001 — Retire Earlier

- **Customer-facing name:** Retire earlier
- **Primary user question:** “What might change if I retire earlier?”
- **Goal type:** Scenario comparison
- **User intent:** Understand whether an earlier date is supportable under explicit spending and
  funding assumptions.
- **Useful outcome:** A baseline-versus-earlier comparison showing funding, key milestones,
  constraints, confidence, and trade-offs.
- **Minimum Financial Picture:** Current ages and household, target age, life expectancy, current
  cash/investments/pensions, expected savings, retirement spending, material income, and applicable
  access/start-age assumptions.
- **Essential information:** Q-001, Q-002, Q-004, Q-005, Q-008 concepts.
- **Helpful information:** Tax profile, State Pension, asset access rules, material property income,
  and employer-equity policy.
- **Optional information:** Alternative spending bands, legacy preference, or phased work.
- **Workspace evidence:** Comparison, funding timeline, asset trajectory, first-retirement-year
  statement, assumptions, limitations, and confidence.
- **Completion criteria:** Both scenarios validate and the Workspace explains material differences
  without advising which age to choose.
- **Confidence considerations:** Uncertain spending, growth, longevity, pension access, tax rules,
  and missing assets reduce projection or strategy confidence.
- **Follow-up explorations:** Different age, lower/higher spending, changed savings, planned asset,
  or downside assumptions.

## G-002 — Investment Property Decision

- **Customer-facing name:** Explore an investment property
- **Primary user question:** “How would buying this property change my financial outlook?”
- **Goal type:** Planned-asset scenario comparison
- **User intent:** Understand liquidity, income, asset-mix, and retirement effects of including a
  property under declared assumptions.
- **Useful outcome:** Baseline-versus-property comparison with purchase timing, cash impact, income,
  asset value, tax treatment, and limitations.
- **Minimum Financial Picture:** Baseline assets/cashflow plus purchase year, price/funding,
  expected net rent, value/growth assumptions, and ownership where relevant.
- **Essential information:** Q-010–Q-013 concepts.
- **Helpful information:** Q-015 ownership/tax concept, transaction costs, financing, vacancy, and
  maintenance assumptions where supported.
- **Optional information:** Alternative purchase dates or property candidates.
- **Workspace evidence:** Cash timeline, property value/income, baseline comparison, financial
  statements, assumptions, excluded costs, and provenance.
- **Completion criteria:** The planned-asset override validates and material included/excluded
  effects are explicit.
- **Confidence considerations:** Indicative rent, omitted costs, financing, uncertain tax treatment,
  and valuation assumptions materially affect confidence.
- **Follow-up explorations:** Different price/date, no purchase, ownership assumption, spending
  change, or retained liquidity buffer.

## G-003 — Employer Equity Exposure

- **Customer-facing name:** Explore employer-equity exposure
- **Primary user question:** “How does my employer-equity exposure affect the outlook?”
- **Goal type:** Concentration explanation and policy comparison
- **User intent:** Understand concentration over time and compare explicit disposal-policy
  assumptions.
- **Useful outcome:** Generic concentration evidence and scenario comparisons without buy/sell or
  suitability advice.
- **Minimum Financial Picture:** Employer-equity identity/value or units and price, other investable
  assets, expected grants/vesting, FX where relevant, growth assumptions, and current disposal
  policy.
- **Essential information:** Q-018–Q-022 concepts.
- **Helpful information:** Restrictions, taxes not modelled, diversification denominator, and
  liquidity needs.
- **Optional information:** User-selected policy variants or concentration thresholds used only as
  exploratory constraints.
- **Workspace evidence:** Position value, maximum employer-equity and single-position concentration,
  timeline, policy comparisons, denominator definition, assumptions, and limitations.
- **Completion criteria:** Exposure and comparison metrics reconcile to deterministic outputs and
  advice language is absent.
- **Confidence considerations:** Price, vesting, FX, tax exclusions, restrictions, and denominator
  scope affect confidence.
- **Follow-up explorations:** Sell-on-vest variants, different price paths, retirement date, or
  liquidity scenarios.

## G-004 — Higher Retirement Spending

- **Customer-facing name:** Explore higher retirement spending
- **Primary user question:** “What if I spent more in retirement?”
- **Goal type:** Spending scenario comparison
- **User intent:** Understand the effect of a higher net spending target on funding and resilience.
- **Useful outcome:** Baseline-versus-higher-spending comparison with asset drawdown, unfunded years,
  and confidence.
- **Minimum Financial Picture:** Current retirement target, proposed target, retirement timing,
  current assets, expected savings/income, inflation, and life expectancy.
- **Essential information:** Q-008, Q-024, Q-025, Q-026, and Q-009 concepts.
- **Helpful information:** Essential/discretionary split and timing changes where supported.
- **Optional information:** Multiple spending bands or temporary one-off expenditure.
- **Workspace evidence:** Funding composition, liquid assets, first unfunded year if any,
  comparison metrics, assumptions, and limitations.
- **Completion criteria:** Both spending scenarios validate and the effect is explained without
  prescribing a spending level.
- **Confidence considerations:** Spending estimate quality, inflation, longevity, tax, and returns
  affect results.
- **Follow-up explorations:** Lower/higher band, delayed retirement, increased savings, or one-off
  spending.

## G-005 — Cash Decline Explanation

- **Customer-facing name:** Explain a cash decline
- **Primary user question:** “Why does cash fall here?”
- **Goal type:** Explanation
- **User intent:** Reconcile a modelled cash movement to underlying income, spending, purchases,
  tax, and funding stages.
- **Useful outcome:** A traceable explanation of the selected period using existing deterministic
  evidence.
- **Minimum Financial Picture:** A sufficient validated baseline and the year/period being queried.
- **Essential information:** Normally zero new data collection when the Financial Picture is
  sufficient.
- **Helpful information:** Clarification of which chart, year, or scenario the user means.
- **Optional information:** A comparison year or scenario.
- **Workspace evidence:** Cash-origin bridge, annual calculation trace, financial statement,
  recurring income, spending, tax, purchases, withdrawals, assumptions, and limitations.
- **Completion criteria:** Opening cash plus auditable movements reconciles to closing cash and the
  explanation cites deterministic evidence.
- **Confidence considerations:** Confidence follows the underlying Financial Picture and model;
  asking unrelated questions should not be used to inflate completeness.
- **Follow-up explorations:** Compare with baseline, inspect a purchase year, explain tax, or explore
  a temporary assumption.

## Future Candidates — Unvalidated

The following require discovery and user validation before joining the active library:

- Build an emergency-fund buffer.
- Explore a pension-contribution change.
- Compare mortgage repayment and investing.
- Understand education-funding capacity.
- Explore a career break or income change.
- Understand estate or inheritance outcomes.

They are candidates only and must not be treated as approved product scope.
