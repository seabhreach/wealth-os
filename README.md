# Wealth OS

Wealth OS is a deterministic, single-household retirement-planning proof of concept. It projects
annual balances, owner-specific pension and State Pension income, optional estimated Irish tax,
and fixed-order withdrawals through life expectancy. It is for planning illustration only and is
not financial, investment, tax, or retirement advice.

## Installation

Wealth OS requires Python 3.13 or newer.

```shell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
```

## Run the dashboard

The included planning-assumption baseline is at `data/example_household.yaml`.

```shell
.venv\Scripts\streamlit run dashboard\app.py
```

The dashboard loads that file by default. Upload another YAML file to validate and project a
different single household.

## Main assumptions

- All balances, spending, pensions, properties, and withdrawal results are reported in EUR.
- Amazon share prices are configured in USD and converted using a static EUR-per-USD exchange
  rate before values, sale proceeds, withdrawals, concentration, and net worth are calculated.
- Annual savings are added to cash before retirement; ETFs grow at the configured rate.
- Rental income is added to cash. When tax modelling is enabled, annual net rent is allocated to
  explicit beneficial ownership shares for estimated personal tax only.
- Pensions grow, may receive owner-specific contributions, and can draw down only after each
  owner's configured access age. State Pension follows each owner's configured start age.
- Retirement spending is a net household target in start-year EUR and grows with inflation.
- Tax modelling is opt-in. Enabled tax converts recurring income to net income using configurable
  Irish Income Tax, USC, and PRSI planning rules; disabled tax preserves gross-income behaviour.

## Withdrawal order

During retirement, rent, permitted pension drawdown, and State Pension create recurring income.
When tax is enabled, estimated tax is deducted before the net recurring income is applied to
spending. Any remaining gap is funded in this order: cash, ETFs, then retained Amazon shares.
Properties are not sold. If permitted liquid assets are exhausted, Wealth OS records unfunded
spending rather than making balances negative.

## Advisor Mode

Advisor Mode runs reproducible in-memory comparisons for retirement ages, RSU sell/retain policy,
planned rental property, spending, and rental ownership assumptions. It never mutates the saved
baseline and does not make recommendations.

## Development checks

```shell
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m mypy
.venv\Scripts\python -m pytest
```

## What this MVP does not yet model

- CGT and ETF deemed disposal
- Residential Premises Rental Income Relief and filing-level relief claims
- Pension lump-sum tax treatment
- Property transaction costs
- Mortgages
- Vacancy and maintenance detail
- Changing FX rates
- Sequence-of-returns risk
- Monte Carlo simulation
