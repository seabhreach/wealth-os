# Trust and Visual Foundation

## Scope

This sprint strengthened deterministic explanation and visual composition for the recovered v0.3
Experience. Its original property audit was subsequently superseded by the correctness work in
`PROPERTY_CORRECTNESS_AND_RESIDENCE_BOUNDARY.md`.

## Trust audit findings

### G-002 planned property

The original audit reproduced the then-current result but did not detect that rent was both added
to cash and used to reduce withdrawals. A later focused ledger audit demonstrated that defect and
also found untaxed employed-year rent. The corrected property-included path has EUR 4,344,368 final
liquid assets and EUR 5,830,652 planning net worth, versus EUR 3,748,242 and EUR 4,582,118 with the
property excluded. The corrected liquid-assets difference is EUR 596,126.

Important limitations remain visible: the baseline has no mortgage, purchase costs, vacancy or
detailed maintenance schedule. `annual_net_rent` is the configured rent after property expenses;
the model does not expose those expenses separately. The opportunity cost is therefore the
modelled cash purchase under the existing cash/ETF rules, not an alternative financed or
securities-funded purchase. Higher modelled wealth does not mean that purchasing the property is
recommended.

`PropertyScenarioReconciliation` records the corrected facts from two completed projections. The
Experience presents purchase liquidity, rent, tax difference, withdrawals preserved, property
trajectory, final liquidity and final wealth without calculating in the renderer.

### G-005 cash and retirement status

The engine evidence for 2027 is unambiguous: the household member is age 55, remains employed,
annual saving is active, and annual retirement spending is zero. The defect was in the Experience
answer template, which called every selected year a retirement-spending year.

The template now receives the projection row's employment state. Pre-retirement years are labelled
pre-retirement and describe the actual annual trace. The first retirement year (2032, age 60) and
later retirement years retain retirement-funding language. The cash-flow component also exposes
the status and retirement milestone beside the selected-year bridge.

This was an explanation defect only. No funding, spending, employment or retirement calculation
changed.

### G-004 spending basis

`target_retirement_income` is a today's-money annual spending assumption. The engine inflates it
from the 2026 projection start to the first retirement year. A EUR 120,000 input therefore becomes
EUR 135,139.49031168 nominal spending in 2032:

```text
EUR 120,000 x 1.02^6 = EUR 135,139.49031168
```

The calculation is correct and unchanged. The Workspace now distinguishes the temporary
today's-money input from the nominal first-retirement-year comparison, and the Financial Picture
uses the same basis label.

### G-003 employer-equity control

Both simulations were already rerunning, and the deterministic evidence differed: maximum
concentration is 8.8185% under sell on vest and 67.1860% under retain. The interaction appeared
inert because both paths were always rendered identically and selected state appeared only in a
small narrative sentence.

The selected policy is now carried in provenance, answer copy and temporary-scenario context. The
Workspace gives concentration primary visual weight and adds exact employer-equity trajectories.
Changing the control refreshes the selected path while leaving the baseline `sell_on_vest` value
immutable.

## Visual system

The visual foundation uses theme-derived tokens for page, raised and accent-soft surfaces. It
creates hierarchy with answer typography, spacious section rhythm, grouped evidence surfaces,
large key values, restrained accent labels and exact trajectory charts. It avoids KPI card grids,
decorative colour, dense tables and advice signals. Light and dark themes use the same semantic
structure and Streamlit's theme variables for contrast.

## Financial Picture

The first viewport is now a household snapshot rather than the top of a long table. It surfaces
cash, investments, annual saving, planned retirement age and the today's-money retirement-spending
assumption, followed by the existing grouped record. Section-level retirement editing and the
explicit non-persistent proposal flow remain unchanged. No score, completeness percentage or new
calculated total was introduced.

## Goal-specific Workspace compositions

- **G-002**: answer, final liquidity/property/net-worth comparison, exact liquid and property
  trajectories, purchase-year liquidity, rent contribution, tax effect, funding preserved,
  trade-off and limitations. Unsupported financing controls were removed.
- **G-003**: answer, maximum concentration, selected policy, employer-equity trajectories, final
  equity/net worth, denominator and limitations.
- **G-004**: answer, today's-money input, nominal first-retirement spending, exact liquid-assets
  paths, funding outcome and limitations.
- **G-005**: status-aware answer, cash trajectory, retirement milestone and a selected-year visual
  bridge from opening cash through inflows/outflows to closing cash.

G-001 remains the benchmark composition and retains its validated specification and renderer.

## Explain this

G-002 through G-005 now create `ExplainContext` directly from validated evidence references. The
deterministic explainer rejects unknown references and remains scoped to the selected component.
No AI or external model call is present.

## Navigation and review mode

Primary navigation remains Home, Financial Picture and Workspaces. The duplicate Return home
action was removed; Ask Wealth OS remains contextual inside a Workspace. Technical fingerprints,
raw overrides, evidence identifiers, engine version and tax version remain restricted to
`?review=1`.

## Remaining limitations

- The property model lacks financing, explicit transaction costs, vacancy and a separate
  maintenance-expense series.
- The current deterministic explanation templates summarize selected evidence but do not yet
  produce conversational multi-turn explanations.
- Financial Picture proposals are still non-persistent.
- Saved Workspaces remain Streamlit-session illustrations rather than durable records.
- All values remain planning illustrations, not forecasts or regulated advice.
