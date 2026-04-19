# Research Workflow

## Goal

This workflow is designed to keep strategy research reproducible and operationally sane.

It covers:

- historical data preparation
- backtesting
- hyperparameter optimization
- bias validation
- dry-run review
- daily reporting

## Recommended Order

1. Download data
2. Run backtest and archive the report
3. Run constrained hyperopt
4. Re-backtest the selected parameter set
5. Run lookahead-analysis
6. Run recursive-analysis
7. Start dry-run
8. Generate daily reports
9. Review for promotion to live

## Commands

### Download data

```powershell
.\scripts\download_data.ps1 -Timerange 20230101-
```

### Backtest

```powershell
.\scripts\run_backtest.ps1 -Timerange 20230101-
```

### Hyperopt

```powershell
.\scripts\run_hyperopt.ps1 -Timerange 20230101- -Epochs 200
```

### Validation

```powershell
.\scripts\validate_strategy.ps1 -Timerange 20230101-
```

### Daily dry-run report

```powershell
.\scripts\daily_report.ps1 -Mode dryrun
```

## Research Rules

- Keep optimization spaces narrow
- Never promote parameters directly from a single hyperopt run without re-backtesting
- Compare in-sample and out-of-sample results
- Review monthly and daily breakdowns, not just total profit
- Reject parameter sets that only improve through lower trade count or unstable behavior

## Suggested Timerange Split

Example:

- in-sample: `20230101-20241231`
- out-of-sample: `20250101-20260331`

Use the same strategy and pair universe across both runs unless you are intentionally testing a structural change.
