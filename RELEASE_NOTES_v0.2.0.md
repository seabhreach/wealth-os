# Wealth OS v0.2.0

## What it does

v0.2.0 adds deterministic Advisor Mode, owner-specific pension drawdown and State Pension timing,
and opt-in Irish planning-tax estimates. Rental profit can be allocated to explicit Decimal
beneficial-ownership shares. When tax modelling is enabled, retirement spending is funded from
net recurring income and then cash, ETFs, and Amazon shares.

## Run it

```shell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\streamlit run dashboard\app.py
```

## Example baseline

The included configuration starts in 2026 with ages 54 and 51, a planned retirement age of 60,
EUR 500,000 cash, EUR 300,000 ETFs, a planned 2027 EUR 200,000 rental-property purchase, and
Amazon grants sold on vest. It enables a 50/50 proposed rental ownership assumption and Irish tax
planning estimates. See [docs/BASELINE_AUDIT_v0.2.md](docs/BASELINE_AUDIT_v0.2.md).

## Limitations

This is a planning illustration, not regulated financial or tax advice. It excludes CGT, ETF
deemed disposal, Residential Premises Rental Income Relief, pension lump-sum treatment,
mortgages, detailed property expenses, changing FX, sequence-of-returns risk, and Monte Carlo.
