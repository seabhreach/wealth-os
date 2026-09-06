# Investment Holding Migration

## Canonical Financial Picture representation

Ordinary taxable investments are represented by immutable `InvestmentHolding` values. Each
holding has a stable holding ID, name, bounded asset type, current EUR value and an optional
security identifier. The supported types are ETF, investment fund, individual equity, bond,
commodity, cryptoasset and other. `OTHER` is the controlled fallback.

Cash, employer equity and real estate remain separate domains. Employer shares and RSUs are not
duplicated as ordinary holdings. An optional security identifier lets an individual-equity
holding retain enough identity for future issuer-level aggregation; this sprint does not add a
new concentration ranking model.

The aggregate taxable-investment value is derived by summing the holdings. It is never stored as
a second balance.

## Legacy ETF input compatibility

The old `etf_value` and `etf_growth_rate` fields are accepted together as input compatibility
only. Before validation, they are migrated to one canonical ETF holding and the shared taxable-
investment growth assumption. They do not appear in the validated model or serialized output.
Mixing either legacy field with canonical holdings is rejected, preventing double counting and
competing financial truth.

The example household is migrated immediately to one EUR 300,000 ETF holding. Its return
assumption and every protected financial output remain unchanged.

## Projection and funding boundary

The engine derives one transient aggregate taxable-investment bucket from the holdings. For now,
all holdings share the existing deterministic growth assumption. This is an explicit engine
limitation, not a claim that ETFs, funds, shares, bonds, commodities and cryptoassets have equal
expected returns.

Retirement funding remains cash, then taxable investments, then retained employer equity. This
sprint does not invent holding-level liquidation order. ETFs contribute to the investable-assets
denominator but are not treated as individual-company exposure. Pensions, investment property and
the inactive primary residence remain outside that denominator.

## Tax limitations

Holding identity does not imply comprehensive asset-specific tax support. The model does not yet
model Irish ETF or fund deemed disposal, CGT on individual shares or cryptoassets, commodity
disposal taxation, or bond-specific taxation. Taxable-investment disposal proceeds remain outside
the current ordinary-income calculation, so after-tax results may be overstated.
