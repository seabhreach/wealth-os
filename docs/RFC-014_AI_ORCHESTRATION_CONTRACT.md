# RFC-014: AI Orchestration Contract

## Status

Approved provider-independent contract and deterministic development stub for Wealth OS v0.3.
No real model provider is integrated in this sprint.

## Purpose

Conversation creates the Workspace. Conversation then controls and explains the Workspace. The
orchestration layer interprets a message and proposes bounded platform operations around existing
deterministic truth. It is not a second financial engine.

The implemented boundary is:

```text
UserMessage + compact selected context
        ↓
OrchestrationProvider.interpret
        ↓
Untrusted OrchestrationResponse
        ↓
schema validation + platform policy validation
        ↓
proposal review/confirmation or validated temporary action
        ↓
deterministic engine/evidence service (not invoked by the provider)
        ↓
WorkspaceSpec + compact evidence slice
        ↓
evidence-grounded explanation
```

`OrchestrationService` is the narrow application integration point. It invokes a provider,
validates the provider response, and emits telemetry. It deliberately does not apply Financial
Picture changes, run scenarios, retrieve evidence, compose a Workspace, or render Streamlit UI.
Those later steps remain platform-owned integration work.

## Responsibilities and non-responsibilities

The provider may classify intent, identify missing information, propose Financial Picture
changes, propose a bounded RFC-013 action, request deterministic evidence, and draft
evidence-constrained language. Its response is always untrusted.

The provider may not calculate projections or tax, invent financial results, execute actions,
mutate persistent state, bypass validation or confirmation, create new action semantics, or make
an authoritative recommendation. Deterministic engines remain the only source of financial
truth. RFC-013 remains the Workspace composition contract.

## Request contract and compact-context policy

`OrchestrationRequest` contains one `UserMessage`, interaction/session identity, optional current
goal and Workspace identity, selected Financial Picture facts, allowed action kinds, relevant
Discovery information requirements, and selected evidence references.

Callers must construct the smallest context sufficient for the current interaction. They must not
send the entire Financial Picture, entire simulation trace, or every Workspace evidence item by
default. Context selection should begin from the current goal and request, then include only:

- relevant facts needed to identify a target or interpret ambiguity;
- allowed actions for the active goal and policy;
- unresolved or material Discovery items;
- evidence references needed to identify an existing result.

Full traces or broader facts require an explicit need and remain deterministic inputs rather than
provider-owned state. Tuple-based immutable fields, bounded enums, and the absence of any raw
simulation field encode this policy in the request schema.

## Response contract

`OrchestrationResponse` contains a typed `ConversationIntent` and zero or more of:

- `FinancialPictureUpdateProposal` objects;
- discriminated deterministic action proposals;
- `MissingInformationRequest` objects;
- one `ExplanationRequest` for deterministic evidence retrieval;
- a user-facing draft;
- ambiguity metadata.

All models are frozen and reject unknown fields. Deterministic actions form a discriminated union
of `SetScenarioValue`, `CompareScenario`, `ResetScenario`, `ExplainEvidence`,
`HighlightEvidence`, `ShowDetail`, `HideDetail`, and `ProposeFinancialPictureUpdate`. The request
also carries the allowed subset, and platform validation rejects actions outside it.

The initial `ScenarioField` vocabulary contains only existing supported goal semantics. A provider
cannot introduce an executable action or arbitrary engine field through free text.

## Financial Picture proposal and confirmation boundary

Ordinary taxable investment proposals embed the canonical engine `InvestmentHolding`; therefore
the existing asset taxonomy validates provider output and remains the sole source of truth.
`FinancialPictureUpdateProposal` records:

- stable proposal and holding identities;
- add, update, or remove operation;
- the bounded taxable-investment target;
- canonical proposed holding value when required;
- user-supplied or user-supplied-estimate provenance;
- validation state and any validation error;
- confirmation required, fixed to `true`.

A proposal object has no reference to mutable application state and cannot apply itself. The
required future flow is:

```text
proposal → display and explicit confirmation → platform validation/application
         → refreshed Financial Picture → deterministic Workspace refresh
```

Significant persistent changes cannot happen silently. The deterministic stub's Bitcoin example
only proposes adding a `CRYPTOASSET` holding with an estimated value; it does not mutate the
Financial Picture.

## Scenario action boundary

Scenario actions are temporary proposals that must pass goal policy and then map to a registered
deterministic override. For “What if I spend €120k?”, the stub emits `SetScenarioValue` for
`annual_retirement_spending = 120000`. It makes no sustainability or funding claim. Only a later
deterministic scenario execution may answer that question.

## Evidence-grounded explanations

For an existing-result question, the provider emits `ExplanationRequest`, containing a bounded
retrieval kind, evidence IDs, and an optional calendar year. It does not receive or create the full
simulation trace.

After platform evidence retrieval, `EvidenceGroundedExplanation` carries compact supplied
evidence and claims. Every claim must cite supplied evidence. Numeric text in a claim is rejected
unless that exact number appears in the supplied evidence payload. Platform validation similarly
rejects numeric claims in the initial user-facing draft unless the value is present in a structured
proposal, action, or evidence request. These checks reduce the risk of unsupported direct numeric
answers; they do not replace deterministic evidence policy or language review.

For “Why does my cash fall in 2032?”, the stub requests the existing G-005 annual statement and
cash trajectory for 2032, with no persistent or scenario mutation.

## Primary-residence protection

The locked rule remains:

> The primary residence is part of the Financial Picture, but not part of the planning portfolio.
> Its value is excluded from investable assets, available cash, retirement funding and strategy
> comparisons unless the user explicitly explores using the residence financially.

The Financial Picture target enum deliberately exposes only ordinary taxable investment
holdings; no residence-availability or planning-capital target exists. For “Could I use the house
to retire at 57?”, the stub recognizes scenario intent but emits no action and no Financial Picture
proposal. It requests an explicit mechanism (downsizing, remortgaging, or equity release), timing,
and costs. Only after those inputs exist may the platform construct a separately validated
deterministic residence scenario. Intent alone never activates home equity.

## Provider abstraction and deterministic stub

`OrchestrationProvider` is a provider-neutral protocol with
`interpret(request) -> OrchestrationResponse` plus provider identity and external-call metadata.
No vendor SDK or transport appears in the contract.

`DeterministicStubProvider` uses simple normalized text matching for four examples: Bitcoin,
higher retirement spending, a 2032 cash explanation, and primary-residence use. Equal requests
produce equal responses. Unknown text produces a clarification response. It uses no local model,
hosted model, network call, API key, projection, or tax calculation.

## Telemetry

`OrchestrationTelemetry` records provider, model, input/output token counts, latency, estimated
cost, interaction and optional session IDs, success, timestamp, and whether an external call was
made. The stub records provider `stub`, no model, zero tokens, zero estimated cost, and
`external_call = false`. This is observability schema only: it is not billing logic and contains no
pricing table.

## Validation and failure behavior

Pydantic schema validation rejects unknown fields, unsupported action discriminators, invalid
investment taxonomy values, inconsistent add/update/remove proposals, and illegal Financial
Picture targets. Platform policy validation rejects actions not allowed by the request, invalid
proposals entering review, and unsupported numeric draft claims. Malformed provider output fails
closed and is never executed.

## Intentionally unimplemented

- any hosted or local model provider;
- provider credentials, API keys, SDKs, transports, pricing tables, or retries;
- billable or network runtime behavior;
- prompt construction and provider-specific token budgeting;
- persistent proposal application and its review UI;
- deterministic scenario execution from proposed actions;
- evidence retrieval and final natural-language generation pipeline;
- residence financing, downsizing, remortgage, or equity-release calculations;
- broad conversation or Workspace UI integration.

These are future, separately reviewed integrations. No real model provider is integrated in this
sprint.
