# RFC-013: Workspace Composition Model

## Status

Approved architecture for future Workspace composition. This RFC defines documentation and
contracts only. It does not implement a renderer, UI components, AI orchestration, engine changes,
or financial behaviour.

## Purpose

This RFC defines how Wealth OS transforms deterministic financial evidence into a highly visual,
question-specific Workspace. A Workspace is not a fixed dashboard. It is a dynamically composed,
reproducible visual answer to the user’s current question.

The architecture is:

```text
User Question
+ Goal / Intent
+ Relevant Financial Picture
+ Scenario
        ↓
Deterministic Engines
        ↓
Structured Evidence
        ↓
Workspace Composition
        ↓
Validated Workspace Specification
        ↓
Visual Renderer
```

Conversation may subsequently explain or manipulate the Workspace through validated actions.

## Core Principles

> The engine decides what is true. The Workspace Composition layer decides how that truth can be
> represented. AI may help choose the most useful representation, but it cannot create or alter
> financial evidence.

This principle operates with the approved experience relationship:

> Conversation creates the Workspace. Conversation then controls and explains the Workspace.

The renderer is presentation-only. It resolves evidence references, applies approved display
metadata, and lays out validated components. It does not need to understand engine internals and
must not perform financial calculations.

## Scope and Non-Goals

RFC-013 defines:

- a typed, serializable Workspace Specification;
- a bounded visual component vocabulary;
- the boundary between evidence and presentation metadata;
- deterministic composition requirements and policy;
- bounded AI composition authority;
- scenario controls and Workspace actions;
- goal-specific composition contracts;
- reproducibility, responsive, accessibility, and testing requirements.

RFC-013 does not define styling, pixel layout, chart-library selection, production persistence,
LLM orchestration, new financial evidence, engine behaviour, or advice logic.

## Workspace Specification

`WorkspaceSpec` is the validated, serializable contract between composition and rendering. A
conceptual schema is:

```text
WorkspaceSpec
- spec_version
- workspace_id
- goal_id
- question
- answer
- scenario
- sections[]
- controls[]
- assumptions[]
- limitations[]
- disclosures[]
- provenance
```

The fields have these responsibilities:

- `spec_version`: version of the Workspace Specification schema.
- `workspace_id`: stable identity for the saved exploration artifact.
- `goal_id`: validated Goal Library identifier or a future validated cross-goal identifier.
- `question`: the customer’s question in their language, with structured intent referenced where
  required.
- `answer`: the required direct-answer component or reference.
- `scenario`: baseline and current temporary scenario identities and validated overrides.
- `sections`: ordered semantic groups containing component specifications.
- `controls`: typed controls mapped to validated scenario actions.
- `assumptions`: material assumption evidence references that must remain available.
- `limitations`: required limitation evidence references that must remain available.
- `disclosures`: secondary component groups and their semantic default state.
- `provenance`: financial-result and presentation-reproducibility metadata.

A valid specification must be possible to:

- schema-validate;
- serialize without renderer state;
- reproduce from saved composition metadata and evidence identities;
- test for policy, references, accessibility, and advice boundaries;
- render without performing financial calculations.

The core specification describes semantic order and grouping. It does not encode desktop grid
coordinates or depend on a particular UI framework.

## Structured Evidence Contract

RFC-013 extends the boundary in
[EXPERIENCE_LIVE_DATA_CONTRACT.md](EXPERIENCE_LIVE_DATA_CONTRACT.md). Each evidence item has:

- a stable evidence ID;
- an evidence type;
- exact value or data;
- units;
- period, date, or timeline context;
- scenario identity;
- source and purpose;
- confidence where applicable;
- provenance and result identity.

Financial evidence is separate from presentation metadata.

```text
Financial evidence
- evidence_id: retirement.age58.final_net_worth
- exact_value: Decimal("1732584.981918750000")
- unit: EUR
- scenario_id: retirement.age58
- provenance: result reference

Presentation metadata
- currency: EUR
- recommended_precision: whole_currency
- compact_display_allowed: true
```

A renderer may display `€1.73m` when policy permits compact display. The underlying exact Decimal
and evidence identity remain unchanged. Recommended formatting is not an alternate financial
value.

Evidence sets are immutable inputs to composition. Missing evidence remains missing: composition,
AI, and rendering must not infer a plausible substitute or fill a live gap with mock evidence.

## Evidence and Component Boundary

Every component that represents financial truth references structured evidence:

```text
ComponentSpec
→ evidence_refs[]
```

For example:

```text
MetricComparison
- baseline_ref: retirement.baseline.final_net_worth
- scenario_ref: retirement.age58.final_net_worth
- label: Net worth at life expectancy
```

Component specifications may contain labels, semantic roles, ordering, disclosure behaviour, and
accessibility metadata. They must not contain independently calculated financial numbers. AI may
select valid evidence references but may not populate arbitrary values into a component.

Validation rejects:

- unknown or inaccessible evidence references;
- evidence from a different Workspace, result, or scenario unless an explicit comparison permits
  it;
- incompatible units or periods;
- a component type that cannot represent the referenced evidence;
- presentation metadata that changes the meaning of evidence;
- omissions of required assumptions, limitations, or provenance.

## Bounded Visual Component Vocabulary

The initial vocabulary is deliberately bounded. Styling and exact chart forms remain renderer
decisions.

| Component | Appropriate when | Inappropriate when |
| --- | --- | --- |
| `ANSWER` | A concise, direct, evidence-backed response can lead the Workspace. | The statement is unsupported, advisory, or substitutes for missing evidence. |
| `METRIC` | One value is material and its unit, period, scenario, and context are clear. | A lone value hides trend, comparison, uncertainty, or denominator. |
| `METRIC_COMPARISON` | Baseline and explored values share compatible meaning, units, and time context. | Values use incompatible definitions, periods, or scenarios. |
| `TIME_SERIES` | Change over time is central and ordered evidence exists. | Only one point exists or time adds no explanatory value. |
| `WEALTH_TRAJECTORY` | A financial trajectory answers a funding, sustainability, or asset-path question. | Aggregate wealth would hide the liquid asset or funding issue being asked about. |
| `TIMELINE` | Ordered life or financial milestones explain access, retirement, State Pension, property, or vesting events. | Event order or dates are unsupported or irrelevant to the answer. |
| `CASH_FLOW` | Inflows, outflows, and funding sources explain a period or transition. | Categories do not reconcile or a chart would imply unsupported causality. |
| `ASSET_MIX` | Relative asset composition materially explains liquidity or exposure. | Categories overlap, the denominator is unclear, or small differences would be misleading. |
| `CONCENTRATION` | A validated numerator and denominator support a concentration measure. | The denominator is absent, invented, or inconsistent across scenarios. |
| `SCENARIO_COMPARISON` | Two validated deterministic scenarios can be compared on common evidence. | Comparison semantics differ or more scenarios would overload the initial answer. |
| `TRADE_OFF` | Evidence shows explicit competing outcomes, including what improves, worsens, or stays unchanged. | It labels a best choice, implies suitability, or lacks evidence for each claim. |
| `INSIGHT` | A deterministic observation is material and cites supporting evidence. | It is speculative, generic, duplicative, or framed as advice. |
| `STRATEGY_OPTION` | A supported nearby exploration can be offered without recommendation. | The option lacks a validated action/override or implies the user should take it. |
| `ASSUMPTION` | A material assumption affects interpretation, confidence, or comparison. | It is irrelevant detail or conceals an unsupported capability. |
| `LIMITATION` | A model, data, or capability boundary affects the answer. | It is omitted for visual simplicity or diluted into generic legal copy. |
| `NARRATIVE` | Short prose explains evidence or connects validated facts. | Prose invents values, unsupported causality, or unnecessary detail. |
| `TABLE` | Exact multi-dimensional comparison or audit detail is genuinely clearer in rows and columns. | A table becomes the default answer or reproduces raw annual output. |
| `DISCLOSURE` | Secondary evidence, assumptions, limitations, or provenance should remain available without dominating. | It hides the direct answer or a material warning needed for correct interpretation. |

New component types require a versioned vocabulary change, policy definition, accessibility
contract, evidence compatibility rules, and tests. AI cannot create arbitrary component types.

## Composition Responsibility

Workspace composition has three layers.

### A. Deterministic requirements

Goal and evidence contracts define what must be present before a composition can be valid. For
example, retirement timing normally requires a funding outcome, retirement-age comparison,
trajectory evidence, and relevant pension milestones. Required evidence does not depend on AI
preference.

### B. Composition Policy

A versioned deterministic Composition Policy defines:

- required and forbidden components;
- evidence-to-component compatibility;
- answer-first ordering;
- maximum initial information density;
- required assumptions and limitations;
- allowed controls and action mappings;
- accessibility metadata requirements;
- advice-language and provenance constraints.

The same policy inputs produce the same validation decision. Policy may permit more than one valid
composition without changing financial evidence.

### C. AI composition

Within the permitted grammar, AI may propose:

- optional components that add explanatory value;
- ordering among optional components;
- explanatory emphasis;
- whether a timeline or trajectory better answers the question when both are allowed;
- evidence to highlight;
- evidence-backed wording.

Every proposal is untrusted input until the platform validates it. The platform may accept,
reject, or replace the proposal with a deterministic fallback composition. AI cannot waive a
required component, introduce a forbidden component, invent evidence, define an override, or hide
a material limitation.

## Rejection of Free-Form AI-Generated UI

Free-form AI-generated UI is not part of the architecture. It creates unacceptable risks:

- invented or altered values;
- inconsistent financial interpretation;
- inaccessible or unusable layouts;
- irreproducible saved Workspaces;
- controls with no supported override;
- excessive information density;
- accidental advice or ranking language;
- hidden assumptions and limitations.

Instead, AI proposes from a controlled visual grammar, the platform validates against versioned
policy, and the renderer renders the resulting Workspace Specification.

## Goal-Specific Composition Contracts

These initial contracts extend the evidence requirements in the live-data contract. “Required”
means a valid Workspace must contain the evidence-backed semantic role when that evidence is
available and the goal can be completed. Unsupported evidence produces an explicit limitation,
not a fabricated substitute.

### G-001 — Retire Earlier

Required:

- `ANSWER` with the funding outcome;
- retirement-age `METRIC_COMPARISON`;
- `WEALTH_TRAJECTORY` or a more relevant liquid-assets trajectory;
- retirement-funding `TIMELINE`;
- relevant pension-access and State Pension milestones;
- material assumptions, limitations, and provenance.

Optional:

- final-wealth comparison;
- bridge-period `CASH_FLOW` or `NARRATIVE`;
- spending sensitivity;
- advice-free `STRATEGY_OPTION` explorations.

Allowed controls: a bounded supported retirement-age control.

### G-002 — Investment Property Decision

Required:

- `ANSWER`;
- liquidity-impact evidence;
- baseline/property `SCENARIO_COMPARISON`;
- rental-income contribution when supported;
- excluded-cost and financing limitations where applicable.

Optional:

- `ASSET_MIX`;
- cash trajectory;
- evidence-backed `TRADE_OFF`.

Allowed controls: include or exclude the configured property. Financing remains unsupported unless
a deterministic engine contract explicitly supports it.

### G-003 — Employer Equity Exposure

Required:

- `ANSWER`;
- employer-equity exposure evidence;
- `CONCENTRATION` only with a validated denominator;
- sell-on-vest versus retain `SCENARIO_COMPARISON`;
- material assumptions, limitations, and provenance.

Optional:

- vesting `TIMELINE` where evidence exists;
- `ASSET_MIX`;
- liquidity-impact comparison.

Allowed controls: supported employer-equity disposal policies. Composition must never invent a
concentration denominator or provider-specific financial meaning.

### G-004 — Higher Retirement Spending

Required:

- `ANSWER`;
- spending `METRIC_COMPARISON`;
- trajectory impact;
- funding or sustainability impact;
- material assumptions, limitations, and provenance.

Optional:

- final-wealth comparison;
- retirement `TIMELINE`;
- evidence-backed `TRADE_OFF`.

Allowed controls: a validated permanent retirement-spending level supported by the scenario API.
The control remains temporary within the Workspace.

### G-005 — Cash Decline Explanation

Required:

- `ANSWER`;
- cash `TIME_SERIES` or cash trajectory;
- selected-year `CASH_FLOW` explanation;
- income and funding-source transition evidence;
- material assumptions, limitations, and provenance.

Optional:

- annual statement `TABLE` within progressive disclosure;
- relevant income or pension `TIMELINE`.

G-005 normally offers no `STRATEGY_OPTION`. Existing evidence should answer the question without
unrelated discovery or invented scenario controls.

## Information Density and Progressive Disclosure

The initial Workspace viewport should normally contain:

- the direct answer;
- one primary visualisation;
- one key comparison.

It should not initially contain ten cards, the full Financial Picture, raw annual tables,
provenance, every assumption, or every available metric. Composition Policy sets bounded component
counts and requires secondary detail to use progressive disclosure.

Material limitations needed to interpret the answer cannot be hidden merely to satisfy density
limits. Disclosures must have understandable labels and remain keyboard and screen-reader
accessible.

## Visual Semantics

Visual meaning is independent of styling:

- baseline and explored scenarios are always explicitly labelled and distinguishable;
- positive and negative meaning never relies only on colour;
- charts identify units, axes, scenario, time context, and evidence scope;
- charts have accessible textual equivalents and data access appropriate to the evidence;
- estimates and material uncertainty are visible;
- display precision does not imply more confidence than the evidence supports;
- comparisons use consistent definitions, periods, units, and denominators;
- missing or partial evidence is distinguished from zero;
- material assumptions and limitations remain reachable from the answer.

## Scenario Controls

`ScenarioControl` is a typed, serializable specification:

```text
ScenarioControl
- control_id
- label
- control_type
- allowed_values_or_range
- baseline_value_ref
- current_value_ref
- action_template
- override_mapping_id
- validation_policy_id
- affected_evidence[]
- accessibility_label
```

Initial control types are discrete choice, bounded numeric, slider, and toggle. Every control maps
through a registered override mapping to a validated temporary scenario request. The specification
does not embed executable code.

```text
Workspace control
→ validated scenario request
→ immutable override
→ deterministic engine
→ new evidence
→ validated Workspace refresh
```

UI controls never mutate engine state or the Financial Picture directly. Baseline value, current
temporary value, allowed domain, and reset behaviour must be explicit.

## Workspace Action Model

Conversation and visual controls converge on the same bounded action model:

- `SetScenarioValue`: set one validated temporary scenario input.
- `CompareScenario`: request a supported comparison against the baseline or current scenario.
- `ResetScenario`: remove temporary overrides and return to baseline.
- `ExplainEvidence`: request an explanation constrained to identified evidence.
- `HighlightEvidence`: focus an existing component or evidence reference.
- `ShowDetail`: open an existing disclosure or permitted detail component.
- `HideDetail`: close secondary detail without deleting evidence.
- `ProposeFinancialPictureUpdate`: create a structured proposal for the separate review and
  confirmation flow.

Actions are typed, serializable, policy-scoped, and validated before execution. AI may propose an
action but cannot execute an unvalidated action or bypass confirmation.

Moving a retirement-age control to 59 and saying “What about 59?” both conceptually produce:

```text
SetScenarioValue
- control_id: retirement_age
- value: 59
```

The same validated action produces the same immutable override, deterministic result, evidence
set, and Workspace state regardless of whether it originated visually or conversationally.

## Evidence-Backed Explanation Contracts

An explanation is a set of claims linked to evidence, not free-standing prose:

```text
ExplanationClaim
- claim_id
- evidence_refs[]
- relationship_ref
- permitted_emphasis
- uncertainty_or_limitation_refs[]
```

For example, explaining that cash falls between retirement and pension access requires references
to employment-income evidence, cash evidence, retirement timing, and pension-access evidence. AI
may phrase the validated relationship naturally. It may not invent causality from coincident
values. When no causal relationship is supported, the explanation must describe only the observed
evidence and limitation.

## Trade-Off Model

A `TRADE_OFF` component explicitly separates evidence-backed outcomes into semantic groups such
as `improves`, `reduces`, and `unchanged`. Each item cites evidence or a validated relationship.

For an age-58 retirement exploration, a valid representation might show:

- improves: two additional years not working;
- reduces: projected liquid assets at 65 and final modelled wealth;
- unchanged: the assumed retirement spending target.

These labels describe the user-directed scenario under declared assumptions. They must not label
a scenario “Best,” “Recommended,” or “Optimal,” and they do not infer suitability.

## Strategy Options

`STRATEGY_OPTION` components are supported explorations, not recommendations. Examples include
retiring one year later, reducing spending, including or excluding a configured property, or
changing a supported employer-equity disposal treatment.

Permitted language includes “Explore,” “Compare,” and “See what changes.” Prohibited language
includes “You should,” “Recommended,” “Best strategy,” and “Optimal choice.” Every option maps to a
validated action and declares its limitations.

## Provenance and Identity

Every Workspace is reproducible. Provenance includes or references:

- Financial Picture fingerprint and baseline identifier;
- scenario identity and immutable overrides;
- assumptions and confidence statuses;
- evidence IDs and evidence-set fingerprint;
- simulation/reporting and tax-rule versions;
- financial result fingerprint;
- Composition Policy version;
- component-vocabulary version;
- Workspace Specification version;
- selected components, semantic order, and evidence references;
- accepted AI composition proposal metadata where it affects structure.

AI wording need not be part of financial result identity. If wording is material to a saved
artifact, the saved Workspace stores or versions that wording separately from financial evidence.

## Determinism and Reproducibility

Two related guarantees remain distinct.

### Financial determinism

```text
Same Financial Picture
+ assumptions
+ scenario
→ same financial evidence
```

Financial determinism is mandatory and independent of presentation or AI composition.

### Presentation reproducibility

A saved Workspace preserves the selected components, semantic order, controls, evidence
references, required disclosures, and relevant disclosure state. It must render the same semantic
artifact later even if a newer AI or Composition Policy could propose a different layout.

Recomposition under a newer policy is an explicit new version, not a silent mutation of the saved
Workspace.

## Responsive Composition

`WorkspaceSpec` describes semantic structure rather than pixel layout. The renderer owns
responsive presentation. A desktop renderer may place a chart and comparison beside one another;
a mobile renderer may place the same chart before the comparison. Component meaning, evidence
references, semantic order, and accessibility do not change.

Core specifications should not encode desktop grid coordinates unless future evidence shows that
reproducibility cannot be achieved without a bounded layout hint.

## Accessibility Contract

Composition contracts support:

- complete keyboard navigation;
- understandable labels and control instructions;
- screen-reader names, descriptions, and relationships;
- chart summaries and textual/data alternatives;
- visible focus;
- sufficient contrast;
- non-colour-only state and comparison meaning;
- logical semantic order across responsive layouts;
- accessible disclosure state and validation errors.

Chart components are invalid without required accessibility metadata. AI cannot generate
arbitrary UI that bypasses this contract.

## Illustrative Workspace Specification

This non-production pseudo-spec intentionally uses evidence references rather than invented
financial values:

```yaml
spec_version: workspace-spec/v1
workspace_id: illustrative-retirement-age-58
goal_id: G-001
question: Could I retire at 58?
answer:
  component_id: answer
  type: ANSWER
  evidence_refs:
    - retirement.age58.funding_outcome
scenario:
  baseline_ref: retirement.baseline
  current_ref: retirement.age58
sections:
  - section_id: primary
    components:
      - component_id: wealth_trajectory
        type: WEALTH_TRAJECTORY
        evidence_refs:
          - retirement.baseline.wealth_trajectory
          - retirement.age58.wealth_trajectory
        accessibility_ref: retirement.wealth_trajectory.summary
      - component_id: retirement_timeline
        type: TIMELINE
        evidence_refs:
          - retirement.age58.retirement_milestone
          - retirement.age58.pension_access_milestones
      - component_id: final_wealth
        type: METRIC_COMPARISON
        baseline_ref: retirement.baseline.final_net_worth
        scenario_ref: retirement.age58.final_net_worth
  - section_id: trade_offs
    components:
      - component_id: retirement_trade_off
        type: TRADE_OFF
        evidence_refs:
          - retirement.age58.work_year_difference
          - retirement.age58.liquid_assets_at_65
          - retirement.age58.final_net_worth
controls:
  - control_id: retirement_age
    type: slider
    allowed_values: [57, 58, 59, 60]
    baseline_value_ref: retirement.baseline.retirement_age
    current_value_ref: retirement.age58.retirement_age
    action_template: SetScenarioValue
    override_mapping_id: scenario.retirement_age
assumptions:
  - retirement.common.material_assumptions
limitations:
  - retirement.common.material_limitations
provenance:
  financial_result_ref: result.retirement.age58
  evidence_set_ref: evidence.retirement.age58
  composition_policy_version: retirement/v1
  workspace_spec_version: workspace-spec/v1
disclosures:
  - assumptions
  - limitations
  - provenance
```

## Illustrative Interaction

```text
User: “Could I retire at 58?”

Conversation checks the Financial Picture and gathers only material missing information.

Discovery Model: Enough Information.

Deterministic engines produce evidence.

Composition validates and renders a Workspace containing the answer, wealth trajectory,
retirement timeline, comparison, trade-off, control, and disclosures.

User moves retirement age from 58 to 59.

SetScenarioValue(retirement_age=59)
→ validated immutable override
→ deterministic calculation
→ new evidence
→ refreshed Workspace

User: “Why is 59 different?”

ExplainEvidence(updated evidence references)
→ validated explanation contract
→ conversational explanation and relevant Workspace highlight
```

This interaction demonstrates Conversation ↔ Workspace ↔ deterministic engine without giving AI
financial authority.

## Validation Pipeline

A proposed Workspace passes through:

1. Workspace Specification schema validation.
2. component-vocabulary validation.
3. evidence-reference and scenario-scope validation.
4. goal-specific required/forbidden component validation.
5. Composition Policy ordering and density validation.
6. control-to-action and override-mapping validation.
7. assumptions, limitations, advice-boundary, and provenance validation.
8. accessibility metadata validation.
9. serialization and reproducibility validation.

Only a validated specification reaches the renderer.

## Testing Strategy

Future implementation requires tests that prove:

- Workspace Specification schema validation accepts valid and rejects malformed specifications;
- all evidence references resolve and unknown references are rejected;
- cross-scenario references require an explicit compatible comparison;
- required goal components are present and forbidden components are rejected;
- scenario controls map only to valid registered overrides;
- equivalent visual and conversational actions produce the same scenario request;
- the renderer performs no financial calculations;
- exact evidence survives compact presentation formatting;
- saved Workspaces remain reproducible across later composition changes;
- required assumptions and limitations cannot be silently omitted;
- AI proposals cannot introduce arbitrary components, evidence, controls, or actions;
- chart components require accessibility metadata and textual alternatives;
- responsive rendering preserves semantic order and meaning;
- financial determinism and v0.2 results remain unchanged.

## Open Questions

These decisions require implementation evidence or user research and remain unresolved:

- How much optional composition authority should AI receive?
- Should Composition Policy be primarily goal-based, evidence-based, or hybrid?
- Which chart types belong in v0.3?
- When should a chart be preferred over a metric?
- How should uncertainty and estimate quality be visualised?
- Should composition change after conversational refinement or favour layout stability?
- How much user customization should saved Workspaces allow?
- Should a Workspace primarily compare baseline plus one explored scenario or support several
  simultaneous scenarios?
- How should charts expose their underlying data?
- What is the right abstraction for cross-goal Workspaces?
- Which disclosure states are semantically important enough to persist?
- When should deterministic fallback composition replace a rejected AI proposal?

## Relationship to Existing Authority

- [RFC-012 Discovery Model](RFC-012_DISCOVERY_MODEL.md) answers: “What information do we need?”
- RFC-013 answers: “How should deterministic evidence be assembled into a visual answer?”
- [RFC-011 Experience](RFC-011_THE_WEALTH_OS_EXPERIENCE.md) answers: “How does the customer move
  through the product?”
- [Conversation and Workspace Model](CONVERSATION_AND_WORKSPACE_MODEL.md) answers: “What are
  Conversation, Workspace, and Financial Picture responsible for?”
- [Experience Live-Data Contract](EXPERIENCE_LIVE_DATA_CONTRACT.md) answers: “How does
  deterministic evidence cross into the Experience layer?”

RFC-013 consumes validated goal, scenario, and evidence contracts. It does not redefine Discovery
Model requirements, Financial Picture truth, engine semantics, or the live-data boundary.

## Relationship to v0.2

The v0.2 engine, simulation, tax, reporting, configuration, and dashboard remain unchanged. This
architecture governs future Workspace composition only and cannot be used to infer new financial
capabilities or semantics.
