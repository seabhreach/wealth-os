# Changelog

All notable changes to Wealth OS are documented in this file.

## [0.2.0] - 2026-08-03

### Added

- Advisor Mode with deterministic retirement, RSU, property, spending, and ownership comparisons.
- Owner-specific pension access, configured pension drawdown, and owner-specific State Pension.
- Opt-in Irish Income Tax, USC, and policy-based PRSI planning estimates with indexed thresholds.
- Beneficial rental-property ownership allocation using Decimal shares and gross-to-net tax reporting.
- Baseline audit, annual reconciliation coverage, and v0.2 release notes.

### Limitations

- No CGT, ETF deemed disposal, rental-income relief, pension lump-sum modelling, mortgages, or
  detailed property expenses.
- No changing FX path, sequence-of-returns risk, Monte Carlo modelling, or regulated advice.

## [0.1.0] - 2026-08-03

### MVP capabilities

- Validates one household configuration from YAML and projects deterministic annual results.
- Models cash savings, ETF growth, Amazon RSUs, rental properties, pension growth, and
  inflation-adjusted retirement spending.
- Converts Amazon USD share values and sale proceeds to EUR using a configured static exchange
  rate.
- Funds retirement spending from rental income and then cash, ETFs, and retained Amazon shares.
- Provides a Streamlit dashboard, retirement-readiness summary, annual projection table, and
  focused automated regression coverage.

### Known limitations

- No Irish taxes, pension drawdown, or State Pension.
- No mortgages, property transaction costs, vacancy, maintenance detail, or property sales.
- No changing FX rates, sequence-of-returns risk, Monte Carlo simulation, or optimisation.
- This software is for planning illustration only and is not financial, investment, tax, or
  retirement advice.
