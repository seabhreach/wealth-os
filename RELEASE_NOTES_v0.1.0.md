# Wealth OS v0.1.0

## What this release does

Wealth OS v0.1.0 is a deterministic, single-household retirement-planning proof of concept. It
loads a YAML configuration, validates it, projects annual household balances through life
expectancy, and presents the result in a Streamlit dashboard. Retirement spending is
inflation-adjusted and funded from rental income followed by cash, ETFs, and retained Amazon
shares.

## How to run it

Wealth OS requires Python 3.13 or newer.

```shell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\streamlit run dashboard\app.py
```

The default configuration is [data/example_household.yaml](data/example_household.yaml).

## Baseline household assumptions

- Primary age 54; spouse age 51; retirement age 60; life expectancy 95; start year 2026.
- Annual retirement spending target EUR 80,000, with 2% inflation.
- Salary EUR 180,000 and annual savings EUR 20,000.
- Cash EUR 500,000; ETFs EUR 300,000 at 6% annual growth.
- Amazon: 310 vested shares, 800 annual grant shares, USD 270 share price, EUR/USD rate 0.92,
  5% annual share-price growth, and sell-on-vest enabled. The opening holding is approximately
  EUR 77,000 before the first year's price growth.
- Pensions: EUR 500,000 and EUR 200,000, each with 4% annual growth and zero contributions.
- One illustrative Lucan rental property: EUR 200,000 purchase/opening value, EUR 16,000 annual
  net rent, and 3% annual growth.

These are planning assumptions, not verified financial or tax advice.

## Model limitations

The model does not include Irish taxes, pension withdrawals, State Pension, property transaction
costs, mortgages, vacancy and maintenance detail, changing FX rates, sequence-of-returns risk,
Monte Carlo simulation, or optimisation. It does not sell property. Retirement readiness assumes
spending is funded from rental income and liquid investments only; pension drawdown and State
Pension are not included.
