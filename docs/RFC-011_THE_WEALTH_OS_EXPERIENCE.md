# RFC-011: The Wealth OS Experience

## Status

Reconstructed product-experience direction. It defines the intended journey beyond v0.2 without
changing the current dashboard or financial behavior.

The staged interaction model recorded below supersedes the earlier UX emphasis in which
Conversation and Workspace continuously evolved as equal side-by-side surfaces during discovery.
It does not supersede the standard navigation model, Financial Picture authority, RFC-012
Discovery Model, deterministic calculation boundaries, or baseline immutability.

## Experience Thesis

Wealth OS begins with a goal or open question, not an inventory form. Conversation helps the user
clarify that question and checks the existing Financial Picture before acquiring only material
missing information. Once enough information exists, Wealth OS creates a visual Workspace that
becomes the primary answer surface. Conversation remains available to control, refine, and explain
that Workspace.

> Conversation creates the Workspace. Conversation then controls and explains the Workspace.

The primary experience sequence is:

```text
Home
→ Conversation
→ Enough Information
→ Workspace
→ Explore through Workspace + Conversation
```

## Standard Views

- **Home** begins with the open goal or question, offers a natural conversation entry point, and
  shows recent Workspaces.
- **Financial Picture** replaces “Inputs.” It is the reviewed, persistent source of truth and
  exposes completeness, confidence, sources, assumptions, and proposed updates.
- **Financial Outlook** replaces “Overview.” It shows the standard deterministic baseline future,
  major drivers, assumptions, and limitations.
- **Strategy Explorer** compares user-selected possibilities, futures, assumptions, and
  trade-offs without recommending an action.
- **Insights** presents deterministic observations worth the user’s attention. An Insight is not
  advice and should link to its evidence.
- **Workspaces** preserve question-focused explanations, visualisations, assumptions,
  comparisons, strategies, and limitations.

“Financial Discovery” may describe the progressive process of understanding relevant information.
The product should not use “Financial Interview”: discovery is adaptive and conversational, not a
script.

## End-to-End Journey

### 1. Open with intent

Home asks what the user wants to explore. A returning user can resume a recent Workspace or ask a
new question. The first screen does not demand completion of the entire Financial Picture.

### 2. Understand the goal

Conversation dominates the interface while it identifies the question, time horizon, household
scope, and desired outcome. It reflects material ambiguity back to the user instead of silently
choosing an interpretation. The Discovery Model remains invisible; the experience must not expose
its Information Items as a questionnaire or one-question-per-item sequence.

### 3. Check the Financial Picture

The Discovery Model determines what is known, missing, material, estimable, unknown, or not
relevant for the goal. It checks existing information before asking anything. One natural response
may satisfy several Information Items. Only material gaps block an initial result.

### 4. Reach Enough Information

**Enough Information** is an explicit experience state reached when the Discovery Model determines
that available information can produce a useful initial answer. The transition should feel
meaningful in conversation—for example, “I have enough to show you what retiring at 58 could look
like.” Wealth OS may transition automatically; it must not require a generic Submit or Continue
action.

### 5. Create the visual Workspace

Wealth OS runs deterministic engines and creates a question-specific Workspace. The Workspace now
uses most or all available width and becomes the dominant interface. It is a visual answer, not a
dashboard or a dump of the Financial Picture. Any estimates and limitations remain visible.

### 6. Explore through the Workspace

Strategy Explorer applies temporary immutable overrides and compares modelled paths. The user can
use relevant visual controls to change an assumption, inspect a trade-off, or return to baseline.
Exploration never silently updates the Financial Picture.

### 7. Continue the conversation

Conversation remains available as a collapsible panel, drawer, rail, or contextual overlay rather
than a permanent peer surface. A follow-up may explain an existing visual, highlight evidence, add
a relevant visualisation, update a temporary scenario, or generate a comparison. Deterministic
engines continue to own all financial truth.

### 8. Preserve the answer

The Workspace records the question, evidence, assumptions, provenance, and limitations. The user
may save or archive it. A proposed material update to the Financial Picture follows a separate
review and confirmation flow.

## Workspace Experience

### Artifact model

Conversation is an interaction. A Workspace is the persistent exploration artifact produced by
that interaction. It represents the user’s question, relevant Financial Picture, temporary
scenario assumptions, deterministic evidence, visual explanation, possible strategies,
limitations, and provenance. It may be saved and revisited, and conversation may continue around
it.

### Visual-first composition

A Workspace is composed for the active question rather than from one fixed dashboard layout. The
default hierarchy is:

1. Answer.
2. Primary visualisation.
3. Key comparison.
4. Why or explanation.
5. Trade-offs.
6. Explore alternatives.
7. Relevant assumptions.
8. Limitations.
9. Provenance.

Retirement questions may use a wealth trajectory, retirement-income timeline, pension-access
milestones, and baseline comparison. Cash-decline questions may use a cash trajectory, annual
funding breakdown, and income-source transition. Employer equity, property, and spending questions
should likewise select only visuals that improve understanding of the current question. All
visuals remain evidence-backed and deterministic.

### Scenario controls

Relevant Workspace controls may explore retirement ages, include or exclude a property, compare
employer-equity disposal policies, or vary spending. These controls create temporary validated
overrides and deterministic results. They never silently mutate the Financial Picture. A permanent
change still follows proposed update → review → explicit confirmation → Financial Picture update.

## Responsive Model

The staged model applies at every width. During discovery, Conversation occupies the screen. After
generation, the Workspace occupies the screen and Conversation can reopen secondarily. Narrow
views must not compress permanent Conversation and Workspace columns beside one another.

## Workspace Composition Authority

[RFC-013](RFC-013_WORKSPACE_COMPOSITION_MODEL.md) defines the bounded visual vocabulary,
deterministic evidence mappings, Composition Policy, AI selection boundaries, validated scenario
actions, provenance, accessibility, and reproducibility requirements for future Workspaces.

## Confidence Model

- **Data Completeness** measures coverage of information required for the current question.
- **Projection Confidence** reflects input quality, assumption stability, and model limitations
  affecting the baseline future.
- **Strategy Confidence** reflects whether compared outcomes are robust enough to distinguish the
  explored paths.

These must remain separate. A complete data set can still support a low-confidence projection,
and a strong baseline projection can still leave a strategy comparison sensitive to one unknown.

## Language and Advice Boundary

Experience copy should say “modelled,” “illustrative,” “under these assumptions,” “compared with,”
and “you could explore.” It should not say “you should,” “recommended,” or imply suitability.
Insights are observations, not instructions. Strategy Explorer describes consequences and
trade-offs, not the action a user ought to take.

Wealth OS is not regulated financial, investment, tax, or legal advice. Professional verification
remains important for material decisions.

## Relationship to v0.2

The v0.2 dashboard provides a validated deterministic baseline and reporting foundation. Future
experience work should adapt those outputs into the concepts above without moving calculations
into the experience layer or altering released semantics implicitly.
