# Conversation and Workspace Model

## Primary Relationship

> Conversation creates the Workspace. Conversation then controls and explains the Workspace.

Conversation and Workspace are not simultaneous peer surfaces during discovery. Conversation is
the interaction that understands intent and acquires material missing information. Workspace is
the artifact created when there is enough information to show something useful. Once created, the
Workspace becomes the dominant exploration surface and Conversation remains available
secondarily.

```text
Home
→ Conversation
→ Enough Information
→ Workspace
→ Explore through Workspace + Conversation
```

## Core Concepts

**Conversation** is the primary interaction model. It captures intent, resolves material
ambiguity, checks what Wealth OS already knows, acquires information naturally, and refines the
user’s question. It may extract multiple Information Items from one response; it does not expose
the Discovery Model as a questionnaire.

**Financial Picture** is the persistent, reviewed source of truth. It contains structured
information, confidence, source, assumptions, and versions.

**Financial Outlook** is the standard deterministic baseline future generated from the Financial
Picture and a declared assumption set.

**Strategy Explorer** compares possible paths using temporary immutable overrides.

**Insights** are deterministic observations grounded in evidence. They are not recommendations.

**Workspace** is a question-focused exploration artifact containing:

- the question being explored;
- the relevant Financial Picture context;
- temporary scenario assumptions;
- deterministic evidence and provenance;
- explanations;
- charts;
- tables;
- assumptions;
- comparisons;
- strategies;
- limitations.

A Workspace is the primary answer surface after generation. It may be saved, revisited, or
archived, but it is not the persistent financial record. Conversation may continue around it to
explain evidence, highlight or add relevant visuals, and apply temporary scenario changes.

## Responsibility Boundaries

| Concept | Responsibility |
| --- | --- |
| AI conversation layer | Owns how to converse, phrase questions, extract proposed information, and explain results. |
| Discovery Model | Owns what information is required, material, sufficient, optional, unknown, or not relevant. |
| Financial Picture | Owns reviewed persistent financial facts, assumptions, confidence, source, and versions. |
| Deterministic engines | Own simulation, tax, reporting, scenario results, and financial truth. |
| Workspace | Owns the structured, visual, question-specific explanation and temporary exploration artifact. |

## Experience States

### State A — Home

Home is a minimal, question-first entry. Recent Workspaces, previously explored goals, and quiet
access to standard views are secondary. Home does not expose discovery mechanics, completeness
meters, configuration, engine terminology, or Financial Picture forms.

### State B — Conversation

Conversation dominates initial discovery. The Discovery Model inspects the existing Financial
Picture first and identifies only material gaps. AI owns how to converse; the Discovery Model owns
what information is needed. The experience does not require one question per Information Item.

### Transition — Enough Information

Enough Information is reached when deterministic requirement evaluation says a useful initial
answer can be produced. The conversational transition should be meaningful and may be automatic;
it does not require a generic Submit or Continue control.

### State C — Workspace

The Workspace becomes the dominant, visual-first interface. Conversation is available through a
secondary panel, drawer, rail, or overlay and acts as controller and explainer for the Workspace.

## Workspace Lifecycle

1. The user asks or selects a question.
2. Conversation understands and confirms intent where ambiguity is material.
3. The Discovery Model checks the existing Financial Picture before any question is asked.
4. Missing material information is acquired naturally; one response may satisfy several
   Information Items, and permitted estimates or assumptions are explicit.
5. The experience reaches Enough Information.
6. Deterministic engines run against the baseline and immutable scenario overrides.
7. Relevant evidence is selected deterministically.
8. A visual Workspace is generated from evidence and provenance and becomes the primary surface.
9. Conversation explains the answer, highlights or adds relevant visuals, or refines temporary
   overrides.
10. The Workspace is saved or archived if the user chooses.

## Workspace Composition and Hierarchy

A Workspace is dynamically composed according to the question:

```text
Question
+ Goal
+ Deterministic Evidence
+ Explanation Needs
→ Workspace Composition
```

The default hierarchy is Answer, Primary visualisation, Key comparison, Why or explanation,
Trade-offs, Explore alternatives, Relevant assumptions, Limitations, and Provenance. Only elements
that help answer the current question should appear. The Workspace must not dump the entire
Financial Picture or expose raw engine structures.

Visuals are question-specific and deterministic. Retirement may need a wealth trajectory and
funding timeline; cash decline may need a cash trajectory and annual funding breakdown; employer
equity may need concentration and vesting visuals; property may need liquidity and allocation
views; higher spending may need a spending delta and sustainability comparison.

[RFC-013](RFC-013_WORKSPACE_COMPOSITION_MODEL.md) defines the bounded visual component vocabulary,
evidence-to-visual mappings, composition authority, AI selection boundaries, provenance,
validated scenario actions, and reproducibility requirements.

## Conversation After Workspace Creation

After generation, Conversation can answer a follow-up, highlight an existing Workspace element,
add a relevant visualisation, update a temporary scenario, or generate a comparison. It does not
replace deterministic evidence or become an independent calculation surface.

Workspace controls may explore nearby validated alternatives such as retirement age, property
inclusion, employer-equity disposal policy, or spending. Their flow is baseline → temporary
scenario → deterministic calculation → updated Workspace.

## Responsive Model

The staged relationship applies on wide and narrow screens. During discovery, Conversation
occupies the screen. After creation, the Workspace occupies the screen and Conversation reopens as
a secondary surface. The conceptual model does not rely on permanent side-by-side columns.

## Baseline Immutability

Exploration follows a strict boundary:

```text
Temporary exploration
→ proposed update
→ user review
→ confirmation
→ Financial Picture update
```

A Workspace must never silently mutate the Financial Picture. Scenario overrides remain local to
the Workspace until the user explicitly proposes and confirms a persistent update. Reverting to
baseline must always be possible.

## Determinism

```text
Same Financial Picture + assumptions + question + scenario overrides
→ same financial results
```

Conversation wording may vary, and evidence layout may adapt to the question, but calculations and
result fingerprints must not. AI-generated text cannot replace or modify engine results.

## Workspace Provenance

Conceptual provenance includes:

- Financial Picture version or fingerprint;
- baseline identifier;
- question or goal;
- scenario overrides;
- assumption set;
- simulation version;
- tax-rule version;
- generated timestamp;
- result fingerprint.

Evidence items should link to this provenance. A later refresh can then explain whether a result
changed because the Financial Picture, assumptions, overrides, or engine version changed.

## AI Boundary

AI may:

- understand and restate intent;
- choose natural wording;
- extract proposed information from conversation;
- explain why information matters;
- select from valid evidence and explanation structures;
- summarize deterministic output and limitations.

AI may not:

- invent a Financial Picture value or confidence status;
- perform authoritative simulation, tax, reporting, or ranking calculations;
- silently confirm a material update;
- alter evidence or provenance;
- turn comparisons into personalized recommendations.

The Discovery Model owns information requirements. Deterministic engines own financial truth. The
Workspace owns explanation.

## Advice Boundary

Workspaces support understanding and exploration, not regulated advice. They must distinguish
observations, assumptions, and user-directed scenarios; avoid suitability or recommendation
language; expose model limitations; and identify where professional financial, investment, tax,
or legal verification may be important.
