# Wealth OS specification (v0.2)

> This document describes the delivered deterministic v0.2 release. The original MVP scope has
> been extended with Advisor Mode, owner-specific pension drawdown and State Pension assumptions,
> and opt-in Irish planning-tax modelling. See `docs/BASELINE_AUDIT_v0.2.md` for audited outputs.

## Released scope

Build a proof of concept that answers whether a single household can retire at age 60 while
maintaining approximately €80,000 of annual spending.

The release uses deterministic annual projections from the configured start year until the
configured life expectancy.

## Scope

The MVP models salary during working years, direct annual investment savings, cash, ETFs,
Amazon RSUs, pension growth, and zero to three rental properties. It presents results in a
Streamlit dashboard.

The original MVP excludes Monte Carlo simulation and estate planning. The v0.2 planning extension
adds opt-in estimated Irish tax on recurring retirement income and owner-specific pension drawdown;
it does not model CGT, ETF deemed disposal, or tax on investment disposals.
AI recommendations, provider integrations, multiple households, multiple scenario comparison,
and mobile applications.

## Inputs

All monetary values are expressed in EUR for MVP v0.1, except the configured Amazon share price,
which is expressed in USD and converted to EUR using the configured static exchange rate.

### Household

- Name
- Primary current age
- Spouse age
- Planned retirement age
- Life expectancy

### Employment

- Salary
- Annual savings, representing the amount invested each year

### Investments

- Cash balance
- ETF value
- ETF growth rate

### Amazon RSUs

- Vested shares
- Annual grant shares
- Share price in USD
- EUR-per-USD exchange rate
- Annual growth rate
- Sell-on-vest policy

### Pensions

One or more pensions each provide:

- Name
- Owner
- Current value
- Annual growth rate
- Annual contribution

Pensions grow and may receive contributions before the household retirement age. They are not
withdrawn during this MVP.

### Rental properties

Each household can have zero to three properties with:

- Name
- Purchase year
- Purchase price
- Current value
- Annual net rent
- Annual growth rate

Stamp duty and legal or purchase costs are excluded from the MVP purchase calculation. A planned
property's purchase price is the only cash outflow modelled at acquisition.

### Assumptions

- Start year
- Inflation rate
- Target retirement income

The retirement target represents desired annual spending, is inflation-adjusted, and ignores
tax calculations.

Amazon share prices are held in USD and converted at the configured static EUR-per-USD exchange
rate before Amazon values, sale proceeds, withdrawals, concentration, and net worth are reported.

## Implemented annual-stage order

Each projection row represents that calendar year's final balances. The projection applies the
following order in every year:

1. Start from the prior year's closing balances; the first row starts from configured opening
   balances.
2. Add the annual savings contribution to cash while employed.
3. Apply ETF growth.
4. Vest the annual Amazon grant while employed, then apply share-price growth.
5. Apply the Amazon sell-on-vest policy at the pre-growth share price, converting sale proceeds
   from USD to EUR at the static
   configured exchange rate.
6. Purchase any property scheduled for the calendar year.
7. Appreciate properties owned before the calendar year; a newly purchased property is not
   appreciated in its purchase year.
8. Add inflation-adjusted rental income to cash.
9. Apply pension growth and, while each owner is working, pension contributions.
10. Calculate the inflation-adjusted retirement spending target after retirement.
11. Fund the spending gap from cash, then ETFs, then retained Amazon shares; pensions and
    properties are not withdrawn or sold.
12. Recalculate final asset balances, Amazon concentration, liquid assets, and net worth.

Retirement spending is an inflation-adjusted net household target. Rental income reduces the
spending gap because it is already added to cash. No optimisation occurs in the MVP.

### Retirement-age what-if convention

The dashboard may temporarily override the configured retirement age for a what-if projection.
This does not change the saved configuration or exported YAML. A person is employed only when
their age is strictly below the selected retirement age. Therefore, when the selected age equals
the configured current age, the opening projection row is a retirement year: salary and annual
savings are zero, retirement spending begins immediately, and no working-year RSUs vest.

## Delivered outputs

The Streamlit dashboard displays configuration status, current position, retirement readiness,
net-worth and liquid-asset projections, retirement cashflow, Amazon exposure, rental-property
values and income, pension values, and an annual projection table. It also displays a
plain-English first-retirement-year funding breakdown, funding composition over time, a selected
year's reporting-only calculation trace, a selected retirement-year income and asset-movement
statement, a cash-origin bridge and Amazon RSU audit, assumptions used, model formulas, limitations, and
clearly flags unfunded years.

## Release verification

- YAML configuration is loaded and validated before projection.
- A deterministic annual projection is produced through the configured life expectancy.
- Streamlit presents the delivered projection and reporting outputs.
- Automated tests cover the simulation stages and documented golden baseline checkpoints.
- No placeholder calculations are present in the completed MVP stages.
