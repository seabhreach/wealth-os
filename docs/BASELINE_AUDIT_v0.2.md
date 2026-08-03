# Wealth OS v0.2 baseline audit

This audit was generated from `data/example_household.yaml` using the deterministic projection.
All displayed monetary values are rounded to whole EUR; calculations retain Decimal precision.
Tax modelling is enabled, future thresholds are indexed by the configured 2% inflation assumption,
and the planned Ardfield Court ownership split is 50% Justin / 50% Wife.

## Calculation and funding order

Each year applies cash savings, ETF growth, Amazon growth/vesting, property purchase/appreciation
and rent, pension growth/contributions, pension drawdown, State Pension, estimated tax, and then
funds the remaining net spending gap from cash, ETFs, and Amazon shares. Property is not sold.

## Checkpoints

| Year | Ages (Justin/Wife) | Recurring income | Tax | Spending | Liquid funding | Closing assets (cash / ETF / Amazon / pensions / property) | Net worth |
|---|---:|---:|---:|---:|---:|---|---:|
| 2026 | 54 / 51 | €0 | €0 | €0 | €0 | €718,720 / €318,000 / €80,854 / €700,000 / €0 | €1,817,574 |
| 2027 | 55 / 52 | €16,000 rent | €0 | €0 | €0 | €763,376 / €337,080 / €84,897 / €728,000 / €200,000 | €2,113,353 |
| 2032 | 60 / 57 | €17,665 rent; €25,306 Justin pension | €4,588 | €90,093 | €51,709 cash | €1,820,897 / €451,089 / €108,352 / €860,417 / €231,855 | €3,472,610 |
| 2035 | 63 / 60 | €18,747 rent; €36,572 private pensions | €6,962 | €95,607 | €47,251 cash | €1,720,979 / €537,254 / €125,431 / €877,718 / €253,354 | €3,514,737 |
| 2038 | 66 / 63 | €19,894 rent; €36,396 private pension; €19,024 Justin State Pension | €10,659 | €101,459 | €36,804 cash | €1,643,484 / €639,878 / €145,203 / €873,512 / €276,847 | €3,578,924 |
| 2041 | 69 / 66 | €21,112 rent; €36,222 private pensions; €40,376 State Pension | €14,820 | €107,669 | €24,780 cash | €1,603,123 / €762,106 / €168,090 / €869,326 / €302,518 | €3,705,163 |
| 2067 | 95 / 92 | €35,329 rent; €34,745 private pensions; €67,566 State Pension | €18,945 | €180,176 | €61,482 cash | €1,226,391 / €3,467,110 / €597,673 / €833,876 / €652,408 | €6,777,458 |

Justin's private pension first draws in 2032, Wife's in 2035, Justin's State Pension begins in
2038, and Wife's begins in 2041. Cash remains positive through life expectancy. Consequently,
there is no ETF-sale year or Amazon-sale year in this baseline.

## First retirement-year worked tax example

In 2032, gross recurring income is €42,972: €17,665 rent and €25,306 Justin private pension.
The 50/50 ownership allocation gives €8,833 rental profit to each person. Estimated Income Tax is
€4,090, USC is €498, and PRSI is €0. Net recurring income is €38,384, so €51,709 is funded from
cash to meet the €90,093 spending target. State Pension is not yet payable.

State Pension is included in Income Tax income and excluded from USC. Cash withdrawals, ETF sales,
and Amazon sales are excluded from ordinary income tax. Pension and rental PRSI are disabled in the
baseline. Future indexed thresholds are an assumption, not a forecast of tax law.

## Ownership worked examples

| Ownership assumption | Estimated household tax in 2032 | Difference vs 50/50 |
|---|---:|---:|
| 100% Justin / 0% Wife | €4,853 | +€265 |
| 50% Justin / 50% Wife | €4,588 | €0 |
| 0% Justin / 100% Wife | €4,543 | -€44 |

The outcomes are non-linear because the model applies joint assessment, household credits, and
individual USC bands. These planning assumptions must match actual beneficial ownership; this is
not a tax-structuring recommendation.

## Tax-disabled comparison

With the same inputs and tax modelling disabled, first-retirement liquid funding is €47,121 rather
than €51,709. Final liquid assets are €5.81m rather than €5.29m, and final net worth is €7.30m
rather than €6.78m.

## Reconciliation status

Automated release-audit tests verify every annual cash, ETF, pension, tax/funding, and net-worth
reconciliation within `0.00000000000000000001` EUR Decimal tolerance. They also verify YAML
round-trip identity, configuration immutability for Advisor scenarios, and deterministic ownership
comparisons.

## Performance sample

On the release workstation, averaged within one Python process: the tax-enabled baseline projection
took 16.85 ms; the tax-disabled equivalent took 9.27 ms; and the complete default Advisor scenario
set took 135.03 ms. These are indicative development measurements, not a performance guarantee.

## Limitations

No CGT, ETF deemed disposal, Residential Premises Rental Income Relief, pension lump-sum modelling,
mortgage modelling, detailed property expenses, changing FX path, sequence-of-returns risk, Monte
Carlo simulation, or regulated financial or tax advice are included.
