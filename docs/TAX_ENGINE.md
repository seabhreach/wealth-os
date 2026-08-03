# Irish tax engine and retirement-funding integration (v0.2 Task 3B)

This is an estimated Irish tax based on configured planning assumptions. It is not a tax return or
tax advice. The engine supports
joint assessment, configurable Income Tax rates/bands/credit, individual USC, and an optional
PRSI policy. State Pension is included in Income Tax income and excluded from USC; private pension
and configured rental profit are USC-liable. Cash, ETF, and Amazon asset sales are excluded.

Rules are loaded from `data/tax/ireland_2026.yaml`. The 2026 inputs use Revenue's published tax
rate-band and USC guidance, retrieved 2026-08-03.

## Projection integration

Tax modelling is opt-in. YAML without a `tax` section remains tax-disabled and retains the former
gross recurring-income funding behaviour. The example household explicitly enables it with joint
assessment and a 50/50 proposed beneficial-ownership split for Ardfield Court.

For a retirement year, Wealth OS grows assets and generates rent; calculates permitted private
pension drawdown and State Pension income by each owner's age; allocates annual net rent to the
property's Decimal ownership entries; calculates household tax; applies net recurring income to
the net spending target; then draws cash, ETFs, and Amazon shares for any remaining gap. Any net
recurring surplus remains in cash. Rent is credited to cash by the property stage, while private
and State Pension income are credited once by the retirement-funding stage and estimated tax is
deducted once.

Tax rules are indexed without intermediate rounding when enabled: for year `Y`, every euro band,
cap, threshold, and credit is multiplied by `(1 + inflation_rate) ** (Y - base_tax_year)`.
Percentage rates do not change. This is a planning assumption, not a prediction of future law.

Known limitations: no CGT, ETF deemed disposal, Residential Premises Rental Income Relief, pension
lump-sum tax treatment, or tax on investment disposals. The example baseline disables pension and
rental PRSI; a configured PRSI rate is used only when the matching policy toggle is enabled.

## Dashboard presentation

The Retirement page presents a gross-to-net bridge, person-level income and estimated-tax table,
and retirement-year charts for gross income, tax composition, and effective rate. The Details page
repeats the selected-year calculation with its configuration assumptions and limitations. Advisor
Mode compares temporary 100/0, 75/25, 50/50, 25/75, and 0/100 rental ownership assumptions without
changing saved configuration. These are planning comparisons only: ownership must reflect actual
legal and beneficial ownership and is not a tax-structuring recommendation.
