# G-001 Visual Workspace Prototype

## Purpose

This prototype applies the RFC-013 composition model to one question:
“Could I retire at 58?” It tests whether a deterministic Wealth OS result can be
presented as an answer-first, visual Workspace rather than as a dashboard or a
permanent Conversation/Workspace split.

The prototype is intentionally bounded to G-001. It does not introduce a general
composition engine, persistence, advice, AI orchestration, or changes to the v0.2
financial model.

## Route and state

The Workspace can be opened from the Retire earlier choice in Live deterministic
mode. A direct review route is also available at:

`experience/app.py?workspace=g001`

The default explored retirement age is 58. The only interactive scenario control is
retirement age, bounded to the deterministic policy’s supported ages (57–61 for the
recovered example household). Each selection maps to the existing
`ScenarioOverride.retirement_age` input. The baseline retirement age remains 60 and
is never mutated or persisted.

## Composition

The fixed G-001 grammar is:

1. Direct answer
2. Liquid-assets trajectory
3. Compact baseline/explored comparisons
4. Retirement bridge timeline
5. Trade-off summary
6. Deterministic “Why?” explanation
7. Collapsed assumptions, supporting figures, limitations, and provenance

`WorkspaceSpec` is a small, immutable and serializable renderer contract. Components
contain evidence identifiers rather than financial values. The G-001 policy validates
section order, component order, the answer-first rule, all evidence references, and
the single registered control before rendering.

Composition identity is recorded separately from financial-result identity:

- Workspace specification: `workspace-spec/v1`
- G-001 composition policy: `g001-visual-workspace/v1`

## Primary visual evidence

The principal chart compares annual liquid assets for the unchanged baseline and the
temporary retirement-age scenario. Liquid assets were selected because they directly
show the bridge between stopping employment and pension income beginning. Net worth
remains a compact comparison rather than the primary visual.

Every plotted point is copied from an existing completed `ScenarioResult.projection`.
The Experience does not interpolate, forecast, recompute, or derive a new financial
metric. Colour, dash style and marker shape distinguish the two paths, and exact values
remain available on hover and in the supporting disclosure.

The timeline uses existing projection fields to identify:

- explored retirement
- baseline retirement
- first private-pension income
- first State Pension income

The comparison rows show retirement age, existing funding status, liquid assets at
life expectancy, and final modelled net worth. The trade-off wording compares existing
results and describes what was held constant; it does not recommend an age.

## Evidence and provenance

The live service continues to adapt only validated configuration and existing v0.2
reporting/simulation results. The Workspace records:

- baseline identifier
- Financial Picture fingerprint
- temporary scenario overrides
- simulation version
- tax-rule identifier
- deterministic result fingerprint
- composition policy version
- Workspace specification version

Assumptions, limitations, supporting figures and provenance are secondary disclosures
so that the direct answer and main evidence remain visually dominant.

## Presentation and accessibility

The Workspace is full-width and uses normal document flow. It avoids KPI-card grids
and the prior permanent split-pane treatment. It is designed to remain stable at
approximately 1440, 1100 and 850 pixels. At narrow widths comparison rows and timeline
milestones stack without changing their semantic order.

The chart has normal-text context, two non-colour visual distinctions, explicit axis
labels, and exact hover values. The age selector uses a labelled native Streamlit
control and is keyboard accessible. Theme-aware tokens preserve contrast in light and
dark modes.

## Unresolved UX questions

- Should the retirement bridge eventually annotate the trajectory directly, or remain
  a separate semantic timeline for clarity at narrow widths?
- Is liquid-assets-at-life-expectancy the most useful compact comparison, or would an
  already-supported bridge-year value better serve customers once broader research is
  available?
- Should a future Conversation transition into this Workspace retain a small visible
  question history, or disappear completely once the answer is composed?
- Does the age control need an explicit undo affordance in addition to selecting the
  baseline age, once scenario persistence exists?

These questions are intentionally deferred. Resolving them is not required to validate
the deterministic composition model and must not introduce new financial evidence.

## Validation boundary

Focused tests cover:

- typed, immutable and serializable composition
- answer-first and fixed-order policy validation
- rejection of unknown evidence references
- mapping of the age action to the existing scenario override
- immutable baseline behaviour
- stable and changing result fingerprints
- full exact annual trajectory evidence
- presentation formatting without evidence mutation
- absence of engine imports and financial arithmetic in the renderer
- Streamlit rendering and in-place age refinement

No engine, tax, dashboard, configuration, or financial-calculation code is modified by
this prototype. Financial outputs and semantics remain those of the recovered v0.2
baseline.
