# Wealth OS Experience Prototype

## Purpose

This is the reference customer-experience storyboard for post-v0.2 exploration. The prototype
validates the experience, not the production architecture. Its purpose is to learn whether people
understand and value a staged, conversation-first Wealth OS in which conversation creates a
question-focused Workspace and then controls and explains it.

This document specifies the next prototype direction. It does not claim that the currently
recovered Streamlit prototype already implements the staged interaction model.

## Experience Under Test

- Conversation is the primary interaction during discovery.
- Conversation creates the Workspace; it does not share equal permanent space with an empty or
  premature Workspace.
- Once created, the Workspace becomes the dominant visual answer surface.
- Conversation remains available secondarily to control, refine, and explain the Workspace.
- The initial screen has no dashboard and begins with “What would you like to explore today?”
- Home shows recent Workspaces for returning users.
- Standard views remain available: Home, Financial Picture, Financial Outlook, Strategy Explorer,
  Insights, and Workspaces.
- The Financial Picture is progressive and persistent; Workspace scenarios are temporary.

The prototype should test comprehension, trust, pacing, confidence language, and the transition
between conversation and visual evidence. It should not be treated as proof of production data,
security, orchestration, or engine architecture.

## Three Prototype States

### State A — Home

Home is a minimal question-first entry. The primary focus is “What would you like to explore
today?” Recent Workspaces, previously explored goals, and quiet access to standard views are
secondary. Discovery mechanics, configuration, engine terminology, mock/live terminology,
completeness meters, and Financial Picture forms are not part of the future customer Home.

### State B — Conversation

Conversation occupies the primary surface. The prototype should feel like natural chat rather
than a wizard, questionnaire, or dashboard with chat attached. It inspects the existing Financial
Picture first and asks only for missing information that materially affects the exploration. One
natural response may satisfy multiple Information Items.

The state ends when the Discovery Model reaches **Enough Information**. Conversation makes the
transition meaningful—for example, “I have enough to show you what retiring at 58 could look
like”—and the Workspace may be generated automatically without a generic Submit or Continue
action.

### State C — Workspace

The Workspace occupies most or all available width and is the primary surface. It is a visual
answer to the user’s question, not a fixed dashboard. Conversation remains available in a drawer,
panel, rail, overlay, or another secondary treatment so the user can ask why, explore what-if
questions, and control relevant temporary scenarios.

## Prototype Modes

The original prototype direction supported:

- scripted conversations for repeatable journey testing;
- mock data for controlled experience scenarios;
- baseline data adapted from validated v0.2 outputs;
- predefined Workspaces with representative evidence.

Mock and baseline experiences must be visibly separated. Prototype copy must not suggest that a
mock result is live or calculated for a real user.

## Dynamic Examples

### Retire earlier

The user asks about an earlier age. Conversation gathers only material gaps, then the Workspace
compares baseline and earlier-retirement paths with a wealth trajectory, retirement-income
timeline, pension-access milestones, funding status, assumptions, and limitations.

### Investment property

The user explores including a planned property. The Workspace shows the baseline beside the
property scenario through liquidity before and after, property/cash allocation, rental-income
contribution, and material exclusions such as transaction costs or mortgage assumptions where not
modelled.

### Employer-equity exposure

The user asks about a concentrated employer-equity position. The Workspace shows exposure over
time, employer equity relative to other investable assets, relevant future vesting, explicit
disposal-policy scenarios, and concentration metrics using a declared denominator. It describes
trade-offs without recommending a sale or retention policy.

### Higher retirement spending

The user explores a higher spending target. The Workspace shows how the outlook, funding sources,
unfunded years, spending delta, wealth trajectory, and confidence change under the temporary
assumption.

### Cash decline explanation

The user asks why cash falls in a year. Without collecting new data when the Financial Picture is
sufficient, the Workspace leads with a cash trajectory, annual inflow/outflow explanation, and
income-source transition, with the calculation trace and relevant assumptions available as
supporting evidence.

## Visual Workspace Pattern

Each predefined Workspace should contain:

1. a direct evidence-grounded answer;
2. the primary visualisation;
3. the key comparison;
4. why or explanation;
5. trade-offs;
6. relevant alternative controls;
7. assumptions and confidence;
8. limitations;
9. provenance.

Conversation should be able to add, remove, or refine Workspace evidence without replacing the
Financial Picture or presenting a fixed dashboard as the answer.

Workspace controls may explore bounded nearby scenarios such as retirement age, property
inclusion, employer-equity disposal policy, or spending. They create temporary validated
overrides, run deterministic calculations, and update the Workspace. They do not silently mutate
the Financial Picture. Persistent adoption remains a separate proposed-update, review, and
confirmation flow.

## Responsive Prototype Model

During discovery, Conversation occupies the screen. After generation, the Workspace occupies the
screen and Conversation reopens as a secondary surface. This applies to wide and narrow views; the
prototype should not depend on permanent two-column Conversation and Workspace presentation.

## Workspace Composition Follow-up

A subsequent `WORKSPACE_COMPOSITION_MODEL` task must define visual component types,
evidence-to-visual mappings, composition authority, AI selection boundaries, deterministic
requirements, provenance, scenario-control mappings, and reproducible layouts. The next prototype
may use predefined compositions to validate the staged experience, but this document does not
fully design that architecture.

## Success Criteria

- Users can begin with a goal without understanding financial data structures.
- Discovery feels like natural conversation and uses the existing Financial Picture first.
- Users recognize the Enough Information transition without needing a generic submission action.
- A useful visual Workspace appears before exhaustive data collection.
- Users understand baseline versus temporary exploration.
- Users can explain what a Workspace is and why its result changed.
- Users can use Conversation as a secondary controller and explainer after Workspace creation.
- Wide and narrow journeys work without permanent side-by-side discovery surfaces.
- Confidence and limitations improve trust rather than merely adding warnings.
- Strategy comparisons are understood as exploration, not advice.
- Standard views remain discoverable without interrupting the conversation.

If this prototype succeeds, future engineering work should focus on replacing scripted
experiences with deterministic engines while preserving the customer experience described in this
document.
