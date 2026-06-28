# PricePilot AI

PricePilot AI is a conservative `Freqtrade`-based Binance Spot trading project.

This repository is set up for the workflow:

1. Download market data
2. Backtest and generate reports
3. Run hyperparameter optimization
4. Validate against lookahead and recursive bias
5. Run dry-run
6. Generate daily trading reports
7. Promote to limited live trading

The implementation intentionally stays close to official Freqtrade behavior instead of building a custom order engine.

## Development Check

- 2026-06-29: Cloned into the Codex workspace and confirmed `dev` as the starting branch for vibe coding.

## Scope

- Exchange: `binance` spot
- Engine: `Freqtrade stable`
- Strategy: `BinanceSpotLowFrequencyStrategy`
- Deployment: Docker Compose
- Risk posture: low-frequency, low-concurrency, exchange stoploss, protections enabled

If your real account is on `Binance US`, change `exchange.name` from `binance` to `binanceus` in the config files before use.

## Repository Layout

- [ARCHITECTURE.md](/E:/Code Repo/PricePilot AI/ARCHITECTURE.md)
- [config/base.spot.json](/E:/Code Repo/PricePilot AI/config/base.spot.json)
- [config/dryrun.json](/E:/Code Repo/PricePilot AI/config/dryrun.json)
- [config/live.json](/E:/Code Repo/PricePilot AI/config/live.json)
- [config/private.live.template.json](/E:/Code Repo/PricePilot AI/config/private.live.template.json)
- [infra/docker-compose.yml](/E:/Code Repo/PricePilot AI/infra/docker-compose.yml)
- [user_data/strategies/BinanceSpotLowFrequencyStrategy.py](/E:/Code Repo/PricePilot AI/user_data/strategies/BinanceSpotLowFrequencyStrategy.py)
- [scripts](/E:/Code Repo/PricePilot AI/scripts)
- [docs/runbooks](/E:/Code Repo/PricePilot AI/docs/runbooks)
- [docs/research-workflow.md](/E:/Code Repo/PricePilot AI/docs/research-workflow.md)
- [docs/repository-files.md](/E:/Code Repo/PricePilot AI/docs/repository-files.md)
- [docs/git-workflow.md](/E:/Code Repo/PricePilot AI/docs/git-workflow.md)

## Prerequisites

- Docker Desktop or Docker Engine with Compose
- A Binance Spot account for live trading
- A dedicated API key for the bot

The local Python virtual environment in this repo is used only for local helper scripts. Trading execution is expected to run in Docker.

## Setup

### 1. Bootstrap

Run:

```powershell
.\scripts\bootstrap.ps1
```

### 2. Review configuration

Open:

- [config/base.spot.json](/E:/Code Repo/PricePilot AI/config/base.spot.json)
- [config/dryrun.json](/E:/Code Repo/PricePilot AI/config/dryrun.json)
- [config/live.json](/E:/Code Repo/PricePilot AI/config/live.json)

Adjust:

- pair whitelist
- stake size
- port bindings
- API server credentials
- timezone

Before live trading, create:

```text
config/private.live.json
```

using:

- [config/private.live.template.json](/E:/Code Repo/PricePilot AI/config/private.live.template.json)

### 3. Download data

```powershell
.\scripts\download_data.ps1
```

### 4. Run a backtest and generate a report

```powershell
.\scripts\run_backtest.ps1
```

This writes:

- raw console output to `reports/backtests`
- a markdown summary to `reports/backtests`
- Freqtrade artifacts to `user_data/backtest_results`

### 5. Run parameter tuning

```powershell
.\scripts\run_hyperopt.ps1
```

This writes:

- raw hyperopt output to `reports/hyperopt`
- a markdown hyperopt report to `reports/hyperopt`
- Freqtrade artifacts to `user_data/hyperopt_results`

### 6. Validate the strategy

```powershell
.\scripts\validate_strategy.ps1
```

This runs:

- backtesting
- lookahead-analysis
- recursive-analysis

You can also run the full research sequence in one command:

```powershell
.\scripts\run_research_cycle.ps1
```

### 7. Start dry-run

```powershell
.\scripts\run_dry.ps1
```

Dry-run API / UI is exposed to localhost only on:

- `http://127.0.0.1:8080`

### 8. Generate a daily report

```powershell
.\scripts\daily_report.ps1
```

This reads the dry-run or live SQLite database and creates:

- markdown reports in `reports/daily`
- machine-readable JSON summaries in `reports/daily`

### 9. Promote to live

Only after the strategy survives a meaningful dry-run period:

```powershell
Copy-Item .\config\private.live.template.json .\config\private.live.json
notepad .\config\private.live.json
.\scripts\run_live.ps1
```

Live API / UI is bound to:

- `http://127.0.0.1:8081`

## Recommended Workflow

1. Download `15m`, `1h`, and `4h` data
2. Backtest on in-sample data and archive the report
3. Hyperopt with constrained spaces only
4. Re-backtest without optimization leakage
5. Run lookahead-analysis
6. Run recursive-analysis
7. Run dry-run for at least 14 days
8. Generate daily reports during dry-run
9. Compare dry-run behavior to backtest assumptions
10. Deploy tiny live capital

## Safety Rules

- Start with `dry_run` only
- Do not enable leverage or futures in this repository
- Use a dedicated Binance API key
- Restrict the key to the minimum permissions required
- Keep REST/FreqUI on `127.0.0.1`
- Never commit `config/private.live.json`
- Run live with capital you can fully afford to lose

## Notes

- The strategy is intentionally conservative and low-frequency. It is closer to a real spot deployment baseline than the initial simple trend example, but it is still not an alpha guarantee.
- Binance Spot Testnet exists, but this scaffold defaults to dry-run because that is the cleaner first validation stage for Freqtrade.
- Hyperopt should be treated as model selection support, not as proof that a parameter set is robust.
- No profitability claim is implied by this project structure.

## Branching

- `main`: stable baseline branch for reviewed work
- `dev`: integration branch for ongoing implementation and experiments

Follow [docs/git-workflow.md](/E:/Code Repo/PricePilot AI/docs/git-workflow.md) as the fixed branch workflow for this repository.

Use [docs/repository-files.md](/E:/Code Repo/PricePilot AI/docs/repository-files.md) as the file-level reference for the repository.
