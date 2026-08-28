# Wealth OS Product Vision

> “Most financial software starts by asking who you are. Wealth OS starts by asking what you're
> trying to achieve.”

## Mission

Help people make better financial decisions by helping them understand and explore their
financial future.

Wealth OS should turn a financial question into an understandable view of possible futures. It
should make assumptions visible, distinguish facts from estimates, and help people explore
trade-offs without pretending that a model can decide what matters to them.

## Product Model

Conversation creates the Workspace. Conversation then controls and explains the Workspace.

The primary experience is staged:

```text
Home
→ Conversation
→ Enough Information
→ Workspace
→ Explore through Workspace + Conversation
```

Conversation is the primary interface while Wealth OS understands the question and acquires only
material missing information. Once sufficient information exists, the Workspace becomes the
primary answer surface. It brings together the visualisations, explanations, comparisons, and
strategies needed to answer the user’s current question. Conversation remains available as a
secondary controller and explainer for that artifact.

The **Financial Picture** is the persistent source of truth: the people, goals, resources,
commitments, assumptions, confidence, and provenance that the user has reviewed. The **Financial
Outlook** is the standard baseline future produced from that picture. The **Strategy Explorer**
compares possible paths, assumptions, and trade-offs. **Insights** are observations grounded in
deterministic results. **Workspaces** are question-focused answer surfaces that assemble the
evidence needed for the current conversation. A Workspace is an artifact that may be saved,
revisited, and explored further; conversation is the interaction that creates and changes it.

Wealth OS does not conduct scripted interviews.
It conducts natural conversations guided by a deterministic Discovery Model.
The AI decides how to ask.
The platform decides what information is required.

## Principles

### Start with goals, not forms

Begin with what the person wants to understand or achieve. Ask only for information that is
material to that question, and explain why it matters.

### Conversation is the primary interface

People should be able to express uncertainty, revise a goal, ask a follow-up question, or change
an assumption naturally. Conversation is not a decorative layer over a form. During initial
discovery it should dominate the interface and feel like a natural exchange, not a visible
questionnaire or a dashboard paired with chat.

### Workspaces are the primary answer surface

An answer may need a short explanation, chart, comparison, assumption, limitation, and supporting
table. A Workspace assembles those elements around one question instead of forcing every answer
into a fixed dashboard. It appears when Wealth OS has enough information to show something useful,
then normally becomes the dominant surface.

### Show financial questions visually when it improves understanding

Wealth OS should show financial questions visually whenever visual representation improves
understanding. Visuals are selected because they help answer the current question, not because the
product needs a generic dashboard. A retirement question may need a wealth trajectory and funding
timeline; a cash question may need a cash trajectory and annual funding breakdown. The composition
must remain evidence-backed and reproducible. The bounded composition architecture is defined by
[RFC-013](RFC-013_WORKSPACE_COMPOSITION_MODEL.md).

### Financial Picture is the persistent source of truth

Exploration never silently changes the Financial Picture. Material proposed updates are shown to
the user and require confirmation. The source, confidence, and effective version of important
information remain visible.

### Show value before asking for more information

Produce the earliest useful outlook that the available information supports. Then explain how an
additional detail would improve confidence, unlock a comparison, or change the answer.

### Every question earns its place

A question must have a clear purpose, be material to the active goal, and unlock a defined result
or improve confidence. Known, irrelevant, or safely estimable information should not be requested
again. Before asking anything, Wealth OS checks the existing Financial Picture. It may extract
multiple Information Items from one natural response and asks again only when missing information
materially affects the requested exploration.

### Strategy Explorer supports exploration, not advice

Strategy Explorer shows how futures change under explicit assumptions and user-selected actions.
It may compare outcomes and constraints, but it does not recommend a product, transaction, or
course of action. Preferences and trade-offs belong to the user.

### Deterministic financial engines own calculations

Simulation, tax, reporting, and decision metrics must be produced by versioned deterministic
engines. The same validated inputs and overrides must produce the same financial result.

### AI may orchestrate, explain, and converse, but must not invent financial truth

AI can understand intent, propose information updates, select relevant evidence, and explain
results. It cannot fabricate balances, calculations, tax treatment, confidence, or engine output.
Uncertainty must be surfaced rather than filled with plausible prose.

### Professional verification remains important

Models simplify reality and laws change. Material tax, legal, investment, pension, and regulated
financial decisions may require verification by an appropriately qualified professional.

## Trust and Confidence

Wealth OS distinguishes three ideas:

- **Data Completeness**: whether the Financial Picture contains the information needed for the
  active question.
- **Projection Confidence**: how strongly the baseline outlook is supported by the quality and
  stability of its inputs and assumptions.
- **Strategy Confidence**: how reliably a comparison distinguishes the explored paths, including
  sensitivity to uncertain assumptions.

These measures inform the user; they are not promises of future outcomes.

## Boundaries

Wealth OS is not regulated financial, investment, tax, or legal advice. It provides deterministic
planning illustrations, explanations, and user-directed exploration. It must not use advice
language, conceal limitations, or present a modelled outcome as a forecast or guarantee.

The implemented v0.2 financial behavior remains authoritative for current calculations. This
vision guides future product and experience work; it does not silently amend released financial
semantics.
