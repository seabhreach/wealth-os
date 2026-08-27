# Conversation and Workspace Model

## Core Concepts

**Conversation** is the primary interaction model. It captures intent, resolves ambiguity,
acquires information naturally, and refines the user’s question.

**Financial Picture** is the persistent, reviewed source of truth. It contains structured
information, confidence, source, assumptions, and versions.

**Financial Outlook** is the standard deterministic baseline future generated from the Financial
Picture and a declared assumption set.

**Strategy Explorer** compares possible paths using temporary immutable overrides.

**Insights** are deterministic observations grounded in evidence. They are not recommendations.

**Workspace** is a temporary, question-focused assembly of:

- explanations;
- charts;
- tables;
- assumptions;
- comparisons;
- strategies;
- limitations.

A Workspace is the primary answer surface. It evolves alongside conversation and may be saved or
archived, but it is not the persistent financial record.

## Workspace Lifecycle

1. The user asks or selects a question.
2. Conversation understands and confirms intent where ambiguity is material.
3. The Discovery Model checks the Financial Picture.
4. Missing material information is requested; permitted estimates or assumptions are explicit.
5. Deterministic engines run against the baseline and immutable scenario overrides.
6. Relevant evidence is selected deterministically.
7. A Workspace is generated from evidence and provenance.
8. Conversation refines the question, overrides, or evidence shown.
9. The Workspace is saved or archived if the user chooses.

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
