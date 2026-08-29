# Integrated Experience Shell

## Purpose

The integrated v0.3 shell brings the recovered Conversation and visual Workspace work into one
customer experience. It demonstrates the approved staged relationship without adding an LLM or
changing deterministic financial behaviour:

```text
Home
→ Conversation
→ Enough Information
→ Workspace
→ Explore or explain
```

The quiet persistent destinations are **Home**, **Financial Picture**, and **Workspaces**.
Financial Outlook, Strategy Explorer, Insights, and engineering Review Mode are not promoted into
the primary navigation.

## Product states

### Home

Home begins with “What would you like to explore today?” and the promise that Wealth OS will use
what it already knows and ask only for what matters. Recent Workspaces are reopenable saved work,
not a menu of supported commands.

### Conversation

The initial Conversation occupies the primary page. A bounded deterministic router recognises
obvious natural-language forms of the five validated goals and extracts a supplied retirement age,
retirement-spending amount, or cash-explanation year where applicable. Unsupported input remains
unsupported and never defaults to retirement.

Because the validated example Financial Picture already contains enough information for these
bounded questions, Conversation acknowledges that fact and offers a goal-specific transition into
the resulting Workspace. There is no generic Submit or Continue control. The router is a prototype
bridge, not a replacement for the future AI conversation layer or Discovery Model.

### Workspace

The Workspace is full-width and becomes the primary answer surface. It is never paired with a
permanent Conversation column. “Ask Wealth OS” and component-level “Explain this” actions open a
secondary contextual conversation surface only when requested; closing it restores the singular
Workspace.

G-001 uses the approved visual composition and is the reference presentation. G-002 through G-005
use a restrained interim full-width renderer: direct answer, a meaningful comparison or evidence
block, supported exploration controls, explanation, and one progressive “About this projection”
disclosure. These interim Workspaces are intentionally not presented as final RFC-013 visual
compositions.

## Natural deterministic routing

The pre-AI router supports representative forms of:

- G-001 retirement timing, including explicit ages such as 57, 58, 59, and 61;
- G-002 investment or rental property questions;
- G-003 generic employer shares, RSUs, stock awards, and concentration questions;
- G-004 higher retirement spending, including values such as `100k`;
- G-005 cash decline or cash-fall questions, including an explicit projection year.

Routing identifies intent only. It does not calculate results, infer missing financial values, or
change scenario policy.

## Financial Picture

Financial Picture is a first-class readable view over the existing validated configuration. It
groups actual values into Household, Income & saving, Cash & investments, Pensions, Property,
Retirement, and Planning assumptions. Labels and formatting are customer-facing; internal field
names, raw Decimal representations, and status enums are not exposed.

The bounded edit prototype covers planned retirement age and annual retirement spending. It shows
a **Proposed Financial Picture Update** and requires explicit confirmation. Persistence is not
implemented because the protected baseline is immutable in this recovery phase. Confirmation
records prototype intent only and states that no baseline data changed.

## Temporary exploration versus persistent truth

A Workspace scenario and the Financial Picture remain visibly distinct:

```text
Workspace: retirement age 57 — changed for this exploration
Financial Picture: planned retirement age 60
```

The retirement control maps to the validated `ScenarioOverride.retirement_age` boundary through
the existing scenario action, runs the deterministic engine, and refreshes the same Workspace.
It never mutates the Financial Picture. “Update Financial Picture” creates only a reviewable
proposal.

## Explain this

G-001 supports contextual explanation for the liquid-assets trajectory, key comparison, and
retirement timeline. Each action creates an immutable `ExplainContext` containing:

- Workspace ID;
- component ID and bounded component type;
- temporary scenario;
- exact evidence references;
- optional selection;
- allowed Workspace actions.

The current explanation is deterministic and template-based. It resolves only the evidence
identified by the component context, opens the secondary Conversation surface, and never modifies
financial evidence or scenario state.

The prepared future contract is:

```text
Workspace → Conversation
Explain this → ExplainContext → ExplainEvidence

Conversation → Workspace
What about 60? → SetScenarioValue
Why is 59 different? → ExplainEvidence
Show the biggest difference → HighlightEvidence
```

Free-form AI action generation and execution are deliberately not implemented.

## Customer experience and Review Mode

Normal customer views do not expose mock/live evidence labels, recovery versions, raw scenario
override objects, fingerprints, engine versions, tax-rule identifiers, evidence IDs, composition
policy, or Workspace specification terminology.

Technical provenance remains preserved in the immutable live Workspace models. Adding
`?review=1` to a Workspace route exposes Review Mode diagnostics containing fingerprints, engine
and tax identifiers, raw overrides, evidence IDs, and result identity. Review Mode does not change
the customer information architecture.

## Responsive model

Conversation and Workspace are singular full-width stages at desktop and narrow widths. The
layout does not compress them into columns at 1440, 1100, or 850 pixels. Financial Picture rows
collapse to a single readable column on narrow screens, and existing G-001 comparisons, timeline,
trade-offs, and charts retain their semantic order.

## Known limitations

- The deterministic router supports only five validated goals and explicit phrase families.
- There is no LLM, adaptive wording, or free-form conversational action interpretation.
- Financial Picture update persistence is deferred; confirmation remains non-persistent.
- G-002 through G-005 use interim evidence presentations pending goal-specific RFC-013 visual
  compositions.
- Saved Workspace persistence remains illustrative within Streamlit session state.
- The current Experience uses the validated example Financial Picture rather than user accounts or
  external integrations.

## AI integration boundary

A future AI layer may understand natural wording, propose structured information updates, explain
referenced evidence, and propose bounded Workspace actions. The Discovery Model still owns
information requirements, the platform validates updates and actions, deterministic engines own
financial truth, and Workspace composition remains constrained by RFC-013. AI must not invent
financial values, evidence, confidence, calculations, overrides, or provenance.

## Financial behaviour boundary

This shell changes presentation, deterministic routing, and Experience orchestration only. It does
not change simulation, tax, pension, property, employer-equity, reporting, dashboard, or baseline
configuration semantics. Temporary scenarios continue to use the existing validated engine APIs,
and the protected v0.2 financial outputs remain unchanged.
