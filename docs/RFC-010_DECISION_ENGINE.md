# RFC-010: Decision Engine

## Status

Reconstructed architecture proposal. It defines a future deterministic comparison capability and
does not change the v0.2 simulation or Advisor Mode.

## Purpose

The Decision Engine explores a bounded set of user-authorized possibilities and returns
transparent comparisons. It is an exhaustive-search and ranking component, not an advice engine.
It answers questions such as “which explored candidates satisfy these constraints?” and “what
trade-offs are visible among the non-dominated candidates?”

## Design Commitments

- Search is bounded, deterministic, and exhaustive within the declared candidate space.
- The initial design accepts at most 100 candidates per run.
- Scenario overrides are immutable and never mutate the Financial Picture or baseline config.
- Every candidate uses the same deterministic simulation, reporting, and rule versions.
- Constraints are evaluated explicitly and failures remain explainable.
- Decimal metrics are compared with declared tolerances rather than binary floating-point
  assumptions.
- Ranking uses dominance and a Pareto frontier before any profile-specific ordering.
- Profiles, metrics, tolerances, exclusions, and explanation rules are transparent.
- Output describes comparisons and trade-offs without recommendation or advice language.

## Inputs and Adapters

The engine receives a validated baseline identifier, immutable scenario overrides, a bounded
decision space, constraints, a transparent comparison profile, and engine provenance.

Adapters isolate product language from engine-specific configuration:

- `DecisionVariableAdapter` maps a generic decision variable and permitted values into candidate
  values.
- `ScenarioOverrideAdapter` converts a candidate into an immutable, validated engine override.
- `DecisionMetricsExtractor` converts deterministic simulation/reporting output into generic
  Decimal or categorical metrics.
- `PositionIdentityAdapter` classifies positions consistently, including employer equity,
  concentrated assets, and other investable positions without embedding provider names.

The adapters must be pure or observational. They cannot mutate the baseline or perform hidden
financial calculations.

## Generic Decision Vocabulary

Initial metrics and variables may include:

- `maximum_employer_equity_concentration`
- `maximum_single_position_concentration`
- `employer_equity_value`
- `concentrated_asset_value`
- `equity_compensation_disposal_policy`
- `planned_asset_included`
- `investable_assets`

Concentration is measured against an explicitly defined denominator. Whether pensions, real
estate, cash, restricted assets, or other positions count as investable assets is a product and
methodology decision that must be stated in the profile. The engine must not infer the denominator
from convenient available fields.

## Candidate Generation

1. Validate the declared decision variables and permitted values.
2. Produce their deterministic Cartesian product in stable order.
3. Reject the request if the product exceeds 100 candidates in the initial design.
4. Convert each candidate through `ScenarioOverrideAdapter`.
5. Validate overrides without applying them to the persistent baseline.
6. Deduplicate semantically identical override sets by a stable fingerprint.

There is no random sampling, heuristic search, or model-selected omission in the initial design.
If the space is too large, the user or calling product must narrow it transparently.

## Execution and Constraint Evaluation

Each candidate executes against the same immutable baseline. Results are keyed by a fingerprint
of the baseline, override, assumptions, engine versions, and comparison profile.

Constraints are named predicates over extracted metrics. A constraint result contains the metric,
operator, threshold, tolerance, pass/fail result, and an explanation token. Invalid candidates and
engine errors are distinct from candidates that validly fail a constraint.

Decimal comparisons use profile-declared absolute or relative tolerances. The engine must not
round for ranking merely because the interface displays rounded values.

## Dominance and Ranking

A feasible candidate dominates another when it is no worse on every declared objective within
tolerance and strictly better on at least one. The Pareto frontier contains feasible candidates
that are not dominated.

The engine reports:

1. invalid candidates;
2. valid candidates that fail constraints;
3. feasible dominated candidates;
4. the non-dominated Pareto frontier.

A transparent profile may then order candidates for display using named priorities, stable
tie-breakers, and tolerances. This ordering is a presentation aid, not a recommendation. Profiles
must be inspectable and versioned; opaque or AI-generated weights are not permitted.

## Explanation Rules

Explanations are deterministic templates driven by recorded metrics and constraint outcomes. They
may state:

- which override distinguishes a candidate;
- which constraints passed or failed;
- why one candidate dominates another;
- which objectives trade off on the frontier;
- which assumptions or limitations materially affect comparison.

They must avoid “best,” “should,” “optimal for you,” or other advice language unless the statement
is a narrowly defined mathematical property such as “lowest modelled tax among these candidates.”

## Performance

For an upper bound of 100 candidates, total runtime is approximately candidate count multiplied by
one deterministic projection and metric extraction, plus small comparison overhead. The first
implementation should support in-process execution, caching by provenance fingerprint, and
measured time/memory budgets. Parallel execution may be added only if result ordering and
reproducibility remain deterministic.

## Testing Strategy

- Candidate generation, stable ordering, limit enforcement, and deduplication tests.
- Baseline and override immutability tests.
- Adapter contract and position-identity tests.
- Constraint boundary tests using Decimal tolerances.
- Dominance and Pareto-frontier property tests.
- Stable profile ranking and tie-break tests.
- Explanation snapshot tests that prohibit advice language.
- Provenance/fingerprint and cache-equivalence tests.
- Integration tests against deterministic engine fixtures.
- Performance tests at 1, typical, and 100-candidate bounds.

## Non-goals

The Decision Engine does not predict markets, discover unrestricted strategies, select financial
products, infer user preferences, or provide regulated advice. It explores only declared,
validated candidates and reports deterministic evidence.
