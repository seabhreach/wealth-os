# Wealth OS Experience Prototype

## Purpose

This is the reference customer-experience storyboard for post-v0.2 exploration. The prototype
validates the experience, not the production architecture. Its purpose is to learn whether people
understand and value a conversation-first Wealth OS with evolving, question-focused Workspaces.

## Experience Under Test

- Conversation is the primary interaction.
- A Workspace evolves alongside the conversation.
- The initial screen has no dashboard and begins with “What would you like to explore today?”
- Home shows recent Workspaces for returning users.
- Standard views remain available: Home, Financial Picture, Financial Outlook, Strategy Explorer,
  Insights, and Workspaces.
- The Financial Picture is progressive and persistent; Workspace scenarios are temporary.

The prototype should test comprehension, trust, pacing, confidence language, and the transition
between conversation and visual evidence. It should not be treated as proof of production data,
security, orchestration, or engine architecture.

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
compares baseline and earlier-retirement paths, funding, milestones, assumptions, and limitations.

### Investment property

The user explores including a planned property. The Workspace shows the baseline beside the
property scenario, cash impact, income timing, asset composition, and material exclusions such as
transaction costs or mortgage assumptions where not modelled.

### Employer-equity exposure

The user asks about a concentrated employer-equity position. The Workspace shows exposure over
time, explicit disposal-policy scenarios, and concentration metrics using a declared denominator.
It describes trade-offs without recommending a sale or retention policy.

### Higher retirement spending

The user explores a higher spending target. The Workspace shows how the outlook, funding sources,
unfunded years, and confidence change under the temporary assumption.

### Cash decline explanation

The user asks why cash falls in a year. Without collecting new data when the Financial Picture is
sufficient, the Workspace assembles a calculation trace, cash-origin bridge, recurring income,
spending, asset movement, and relevant assumptions.

## Prototype Workspace Pattern

Each predefined Workspace should contain:

1. the user’s question in their language;
2. a direct evidence-grounded summary;
3. the smallest useful visualisation or comparison;
4. assumptions and confidence;
5. limitations and provenance;
6. optional follow-up explorations.

Conversation should be able to add, remove, or refine Workspace evidence without replacing the
Financial Picture or presenting a fixed dashboard as the answer.

## Success Criteria

- Users can begin with a goal without understanding financial data structures.
- A useful answer appears before exhaustive data collection.
- Users understand baseline versus temporary exploration.
- Users can explain what a Workspace is and why its result changed.
- Confidence and limitations improve trust rather than merely adding warnings.
- Strategy comparisons are understood as exploration, not advice.
- Standard views remain discoverable without interrupting the conversation.

If this prototype succeeds, future engineering work should focus on replacing scripted
experiences with deterministic engines while preserving the customer experience described in this
document.
