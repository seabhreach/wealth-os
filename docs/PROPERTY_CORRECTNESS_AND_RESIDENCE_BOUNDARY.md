# Property Correctness and Primary Residence Boundary

## Status

This document records the v0.3 correction applied after the trust audit at commit `15e394d`.
The correction changes demonstrated defective financial outputs; it does not introduce more
conservative property assumptions or activate home equity for planning.

## Rental cash-flow correction

The property stage previously added rent to cash, while the retirement stage also subtracted the
same rent from spending before drawing cash. A receipt could therefore remain in closing cash and
fund spending simultaneously. The focused regression proves that, with no surplus, closing cash
now equals opening cash less the cash withdrawal.

Rent is now carried as recurring income into the funding stage. Net recurring income either funds
spending or, when it exceeds spending, becomes `after_tax_surplus` added to cash. It is never both.
Annual traces expose that surplus explicitly and cash bridges reconcile as:

```text
opening cash + savings + equity-sale proceeds + after-tax surplus
- property purchases - cash withdrawals = closing cash
```

## Employed-year rental-tax correction

Tax calculation previously returned early for every employed year, making 2027–2031 rent tax-free.
The tax input now supports employment income. During employed years the projection calculates tax
on employment plus owner-allocated rent, subtracts the employment-only result, and charges the
marginal difference caused by rent. This uses the existing joint bands, credits and individual USC
rules without charging salary tax against cash: configured annual savings remains the household's
direct cash contribution. Rental PRSI remains disabled.

For the example household, employed-year rent of EUR 83,264.64 produces EUR 24,979.39 Income Tax
and EUR 3,330.59 USC, or EUR 28,309.98 total. The 50/50 beneficial ownership is retained. Justin's
employment income places household income into the higher band; Wife's share also affects the
joint lower-earner band and her individual USC threshold/bands.

## Corrected G-002 reconciliation

| Measure | Property included | Property excluded | Difference |
|---|---:|---:|---:|
| Purchase-year liquidity | EUR 1,179,912.91 | EUR 1,369,352.91 | EUR -189,440.00 |
| Cumulative nominal rent | EUR 1,001,760.37 | EUR 0 | EUR 1,001,760.37 |
| Cumulative incremental rental tax | EUR 227,715.19 | EUR 0 | EUR 227,715.19 |
| Cumulative net rental contribution | EUR 774,045.17 | EUR 0 | EUR 774,045.17 |
| Total retirement withdrawals | EUR 1,547,045.60 | EUR 2,266,136.11 | EUR -719,090.51 |
| Cash withdrawals | EUR 1,547,045.60 | EUR 1,971,676.11 | EUR -424,630.51 |
| Taxable-investment sales | EUR 0 | EUR 294,460.00 | EUR -294,460.00 |
| Employer-equity sales for spending | EUR 0 | EUR 0 | EUR 0 |
| Final cash | EUR 279,585.18 | EUR 0 | EUR 279,585.18 |
| Final taxable investments | EUR 3,467,109.80 | EUR 3,150,568.87 | EUR 316,540.93 |
| Final employer equity | EUR 597,673.29 | EUR 597,673.29 | EUR 0 |
| Final liquid assets | EUR 4,344,368.27 | EUR 3,748,242.16 | EUR 596,126.11 |
| Final pensions | EUR 833,876.05 | EUR 833,876.05 | EUR 0 |
| Final investment property | EUR 652,407.56 | EUR 0 | EUR 652,407.56 |
| Final planning net worth | EUR 5,830,651.87 | EUR 4,582,118.21 | EUR 1,248,533.66 |

The corrected liquid-assets bridge is:

```text
EUR -200,000.00 purchase capital
+ EUR 54,954.66 pre-retirement after-tax rental surplus
+ EUR 719,090.51 retirement liquid withdrawals avoided
+ EUR 22,080.93 taxable-investment timing/compounding interaction
= EUR 596,126.11 final liquid-assets difference
```

Property appreciation remains outside liquid assets. It enters only investment-property value and
planning net worth because no sale occurs.

The old EUR 1,542,931.81 advantage falls by EUR 946,805.70. EUR 918,495.72 is the retirement rent
that previously received double treatment and EUR 28,309.98 is corrected employed-year rental tax.
There is no unexplained residual or additional secondary change in that before/after reduction.

## Remaining property assumptions and limitations

The model continues to assume a EUR 200,000 cash purchase, EUR 16,000 configured annual net rent,
2% rent indexation and 3% property appreciation. Financing, transaction and sale costs, vacancy,
detailed maintenance, management, capital expenditure and residential rental relief remain
unmodelled. Configured annual net rent is used as taxable rental profit. These limitations are
evidence, not guessed adjustments.

## Primary Residence Boundary

The primary residence is part of household position and inactive for planning by invariant. It is
not cash, liquidity, investable wealth, retirement funding, property-purchase capital, investment
property, rental income, or a concentration denominator. Future sale, downsizing, remortgage or
equity release requires a separate typed and validated scenario; no activation switch exists.

`PrimaryResidenceConfig` records a `PRIMARY_RESIDENCE` purpose, estimated market value and mortgage
balance and derives equity. The example home is worth EUR 1.5m and mortgage-free. The Financial
Picture presents it separately with the message that it is in household position but not assumed
available to fund the plan.

Planning net worth preserves the existing projection calculation. Household net worth adds
represented primary-residence equity. Liquid assets, retirement assets, investment-property value
and residence equity remain distinct.

## Concentration denominator

Employer-equity concentration now uses the explicit investable-assets denominator:

```text
cash + taxable investments + employer/direct equity
```

Pensions, investment property and primary residence are excluded. ETFs belong in the denominator
but are diversified funds and are not treated as a single-security numerator. The current model
has one direct employer-equity issuer, whose holdings are aggregated in its projected value.

On the corrected financial projection, the old net-worth denominator would produce maximum
concentrations of 10.25% for sell-on-vest and 77.65% for retain. The corrected denominator produces
13.76% and 87.96%, respectively. The previously displayed pre-correction values were 8.82% and
67.19%; the combined change also reflects the corrected property cash balances.

## Changed golden outputs

The example baseline changes only where the two demonstrated property defects propagate:

- 2027 closing cash: EUR 763,376.00 to EUR 757,936.00;
- 2067 liquid assets: EUR 5,291,173.97 to EUR 4,344,368.27;
- 2067 planning net worth: EUR 6,777,457.58 to EUR 5,830,651.87.

Investment-property value, pensions, employer-equity value, retirement spending, pension income,
State Pension rules and the property-excluded path remain unchanged.

## Deterministic invariants

Regression coverage proves single rental recognition, annual cash reconciliation, marginal
employed-year rental tax, beneficial ownership, configured Income Tax/USC/PRSI treatment, the
RFC-010 denominator, and primary-residence exclusion from every projection result. Residence value
and debt may change household net worth; residence value cannot change planning net worth or any
scenario affordability result.
