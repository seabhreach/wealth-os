# Experience Live-Data Contract

## Status and Purpose

This reconstructed Phase 4 boundary describes how the future experience consumes validated live
financial results. It is an architecture contract, not implemented v0.2 behavior.

## Data Flow

```text
Validated config
→ Financial Picture adapter
→ existing deterministic simulation/reporting APIs
→ immutable evidence adapters
→ Workspace view models
→ Experience renderer
```

The experience layer never performs financial calculations. It receives immutable evidence from
versioned deterministic APIs and chooses how to present that evidence for the active question.

## Boundary Rules

- The validated baseline is read-only during Workspace generation.
- Exploration uses temporary validated overrides only.
- A user must explicitly review and confirm a permanent Financial Picture update.
- Mock and live modes never mix within one result or Workspace.
- Every result retains provenance and a result fingerprint.
- Evidence selection is deterministic for a declared goal, result, and evidence policy.
- View models may format and arrange values but may not calculate financial truth.
- Missing evidence is reported; the experience must not infer or fabricate it.
- Advice-free language and engine limitations travel with the evidence.

## Immutable Evidence Models

The live-data boundary may expose generic immutable models such as:

- `NarrativeEvidence`: deterministic explanation tokens and cited facts;
- `MetricEvidence`: named value, unit, period, precision, and provenance;
- `ComparisonEvidence`: baseline and candidate metrics with declared differences;
- `TimelineEvidence`: ordered milestones or annual values;
- `TableEvidence`: typed rows, columns, units, and footnotes;
- `FinancialStatementEvidence`: reconciled income, spending, tax, and asset movement;
- `AssumptionEvidence`: assumption value, source, confidence, and scope;
- `LimitationEvidence`: unsupported behavior or interpretation boundary;
- `StrategyEvidence`: immutable overrides, constraints, results, and trade-offs;
- `InsightEvidence`: deterministic observation and supporting evidence references.

Evidence models carry identifiers and provenance; they do not contain renderer-specific mutable
state. Formatting must not alter underlying Decimal values.

## Provenance

At minimum, live results identify:

- Financial Picture fingerprint and baseline identifier;
- goal/question identifier;
- immutable scenario overrides;
- assumptions and confidence statuses;
- simulation/reporting version;
- tax-rule version where applicable;
- evidence-policy version;
- generation time and result fingerprint;
- mode: live or mock.

## Goal-to-Evidence Contracts

### G-001 Retire Earlier

Required evidence: validated baseline and earlier-age comparison, retirement/funding milestones,
asset and funding timeline, first-retirement-year statement, assumptions, limitations, and
projection/strategy confidence. No persistent retirement-age change occurs during exploration.

### G-002 Investment Property Decision

Required evidence: baseline and planned-asset comparison, purchase cash movement, property value
and income timeline, asset composition, relevant tax/ownership evidence, excluded costs, and
assumptions. Unsupported financing or cost detail must be a limitation, not an experience-layer
calculation.

### G-003 Employer Equity Exposure

Required evidence: employer-equity and single-position values/concentration, denominator
definition, exposure timeline, explicit disposal-policy candidates, comparison metrics,
limitations, and provenance. Provider-specific concepts remain behind identity adapters.

### G-004 Higher Retirement Spending

Required evidence: baseline and spending-override comparison, funding composition, liquid-asset
trajectory, first unfunded year when present, assumptions, and confidence. The experience cannot
reinterpret net/gross or inflation semantics.

### G-005 Cash Decline Explanation

Required evidence: selected-year opening and closing cash, cash-origin bridge, calculation trace,
recurring income, spending, tax, purchases, withdrawals, financial statement, assumptions, and
limitations. When existing evidence is sufficient, no new Financial Picture data is required.

## Failure and Partial Evidence

Validation errors, engine failures, unsupported scenarios, and incomplete information are distinct
states. A Workspace may show partial evidence only when it clearly states what is missing and does
not present a partial calculation as complete. Mock evidence must never fill a live gap.

## Update Flow

If conversation suggests a persistent change, the experience creates a structured proposed
Financial Picture update with source and confidence. It is validated, displayed to the user, and
applied only after explicit confirmation. The Workspace can then refresh from the new baseline and
retain provenance for both versions.
