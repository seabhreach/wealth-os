# RFC-012: Discovery Model

## Status

Foundational architecture for future conversational discovery. It supersedes the Question Library
as the target architecture; the Question Library remains a transitional prototype and test
artifact.

## Core Principle

AI owns the conversation.
The Discovery Model owns information requirements.
The deterministic engine owns financial truth.
The Workspace owns explanation.

Wealth OS does not conduct scripted interviews. It conducts natural conversations guided by a
deterministic Discovery Model. The AI decides how to ask; the platform decides what information is
required.

## Information, Not Questions

The Discovery Model represents **Information Items**, not fixed prompts. An Information Item is a
structured definition of a fact, estimate, assumption, or status that may matter to one or more
goals. The same item can be acquired by conversation, manual editing, import, or integration and
can be expressed differently depending on context.

Representative Information Items include:

- current age;
- household members;
- retirement age;
- retirement spending;
- cash;
- investments;
- employer equity;
- pensions;
- property;
- tax profile;
- State Pension assumptions;
- expected savings.

This list is illustrative. Item identifiers and semantics must remain stable even as acquisition
wording and interfaces evolve.

## Information Item Contract

Each item conceptually defines:

- stable identifier and purpose;
- customer-understandable description;
- data type, units, cardinality, and time basis;
- confidence requirements;
- whether an estimate is allowed;
- whether unknown is allowed;
- validation rules;
- goals supported;
- related items and dependencies;
- Workspace impact;
- Decision Engine impact;
- deterministic engine usage;
- possible acquisition sources;
- illustrative recognized answers;
- illustrative AI wording.

Recognized answers and wording are examples, not scripts. Validation rules and engine semantics are
deterministic and cannot be changed by conversational phrasing.

## Confidence and Completeness

Each relevant item may have one of these statuses:

- **Verified**: corroborated by an authoritative or reviewed source.
- **Known**: supplied and accepted as current, without external verification.
- **Estimated**: approximate value supplied for exploration.
- **Assumed**: explicit model or baseline assumption rather than a claimed fact.
- **Unknown**: relevant but not currently available.
- **Not Relevant**: determined not to apply in the active scope.

Status is not a simple quality score. An estimate may be sufficient for an early Workspace but not
for a sensitive strategy comparison. “Unknown” is honest data, not an invitation for AI to guess.

Data Completeness is evaluated per goal and question. A complete Financial Picture is not required
before every useful answer, and collecting irrelevant detail must not inflate completeness.

## Information Acquisition

An Information Item may be acquired through:

- conversation;
- manual Financial Picture editing;
- file or structured-data import;
- document extraction;
- bank integrations;
- employer feeds;
- adviser input;
- future APIs.

Every acquisition produces a proposed structured value with source, confidence, effective date,
and validation result. Extraction is not confirmation. Material proposed changes require review
before updating the Financial Picture.

## Conversation Policy

The Conversation Policy uses the active goal, Financial Picture, and Information Item definitions
to determine:

- what is already known;
- what is still needed;
- which gaps are material;
- whether estimates or assumptions are acceptable;
- whether enough information exists to produce useful evidence;
- what optional refinement would improve confidence.

The policy may prioritize items by materiality, dependency, user effort, and value unlocked. It
does **not** prescribe exact wording, a fixed sequence, or a scripted interview. AI owns natural
language within policy and safety boundaries.

## Deterministic Requirement Evaluation

Given the same goal/question, Financial Picture version, and policy version, the Discovery Model
must produce the same required, sufficient, optional, unknown, and not-relevant item states. AI may
explain or ask differently, but it cannot declare an unmet essential item complete.

Dependencies are explicit. For example, a property-ownership item may become essential only when a
supported tax comparison depends on it. A cash-decline explanation should request no new data when
existing engine evidence is sufficient.

## Response Flow

```text
Conversation
→ information extraction
→ validation
→ proposed Financial Picture update
→ confirmation where significant
→ Financial Picture
→ Workspace refresh
```

Temporary scenario values can flow directly into immutable Workspace overrides when the user is
exploring rather than updating baseline facts. The distinction must be visible.

## Boundaries

### AI boundary

AI may extract, phrase, summarize, and explain. It may not invent required values, bypass
validation, silently confirm updates, or perform authoritative financial calculations.

### Engine boundary

Simulation, tax, reporting, and decision engines consume validated structured inputs. They remain
independent of conversational wording and acquisition channel.

### Advice boundary

Discovery exists to support planning illustrations and exploration. It must not infer suitability,
risk tolerance, or regulated advice conclusions from conversational tone. Professional
verification remains important.

## Example Item

An illustrative `retirement_spending` item might be a Decimal annual amount in start-year EUR,
allow known or estimated values, support G-001 and G-004, depend on household scope and value basis,
unlock retirement funding evidence, and feed the deterministic spending target. Conversation might
ask “What annual spending would you like this outlook to support?” but another channel could import
or manually edit the same item. The item—not the sentence—is the architecture.

## Migration Roadmap

1. **Phase 1 — Question Library:** scripted prototype questions validate journeys and terminology.
2. **Phase 2 — Question Library + Discovery Model:** questions map to stable Information Items and
   deterministic requirement states.
3. **Phase 3 — Discovery Model primary:** product logic uses Information Items; Question Library
   remains examples and test fixtures only.
4. **Phase 4 — Adaptive AI conversation:** AI chooses natural acquisition and refinement driven by
   the Discovery Model, while deterministic requirements and confirmation boundaries remain in
   platform control.

## Testing Strategy

- Item-schema, validation, dependency, and status-transition tests.
- Goal-specific minimum/sufficient-information fixtures.
- Determinism tests for requirement evaluation and policy versions.
- Acquisition-source equivalence and provenance tests.
- Estimate/unknown/not-relevant boundary tests.
- Proposed-update confirmation and baseline-immutability tests.
- Conversation contract tests that allow wording variation but prohibit requirement bypass.
- Workspace refresh and result-provenance integration tests.
