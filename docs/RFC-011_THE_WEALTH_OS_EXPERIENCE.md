# RFC-011: The Wealth OS Experience

## Status

Reconstructed product-experience direction. It defines the intended journey beyond v0.2 without
changing the current dashboard or financial behavior.

## Experience Thesis

Wealth OS begins with a goal or open question, not an inventory form. Conversation helps the user
clarify that question and build enough of a Financial Picture to generate an early, useful answer.
The answer appears in a Workspace that evolves with the conversation.

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

The conversation identifies the question, time horizon, household scope, and desired outcome. It
reflects ambiguity back to the user instead of silently choosing an interpretation.

### 3. Check the Financial Picture

The Discovery Model determines what is known, missing, material, estimable, unknown, or not
relevant for the goal. Only material gaps block an initial result.

### 4. Deliver early value

As soon as sufficient information exists, Wealth OS runs deterministic engines and creates a
first Financial Outlook or question-specific Workspace. Any estimates and limitations are visible.

### 5. Refine progressively

Each additional question explains what it unlocks or how it improves Data Completeness,
Projection Confidence, or Strategy Confidence. Users may supply an estimate, mark an item unknown,
edit the Financial Picture, or continue with an explicit assumption where permitted.

### 6. Explore possibilities

Strategy Explorer applies temporary immutable overrides and compares modelled paths. The user can
change an assumption, inspect a trade-off, or return to baseline. Exploration never silently
updates the Financial Picture.

### 7. Preserve the answer

The Workspace records the question, evidence, assumptions, provenance, and limitations. The user
may save or archive it. A proposed material update to the Financial Picture follows a separate
review and confirmation flow.

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
