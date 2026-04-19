# Repository Files

This document describes the purpose of every tracked file in the repository and the main local-only directories around it.

## Top Level

- [README.md](/E:/Code Repo/PricePilot AI/README.md): primary project entry point, setup guide, workflow summary, and branch policy.
- [ARCHITECTURE.md](/E:/Code Repo/PricePilot AI/ARCHITECTURE.md): system architecture, risk model, deployment model, and operational design for the Freqtrade-based trading stack.
- [.gitignore](/E:/Code Repo/PricePilot AI/.gitignore): repository ignore policy for secrets, local runtime data, generated reports, caches, IDE files, and local virtual environments.

## Config

- [config/base.spot.json](/E:/Code Repo/PricePilot AI/config/base.spot.json): shared base configuration for Binance Spot, bot behavior, pricing, pairlist, API server, and default runtime settings.
- [config/dryrun.json](/E:/Code Repo/PricePilot AI/config/dryrun.json): dry-run overrides including simulated wallet and dry-run database path.
- [config/live.json](/E:/Code Repo/PricePilot AI/config/live.json): live trading overrides including live database path and tighter live stake amount.
- [config/private.live.template.json](/E:/Code Repo/PricePilot AI/config/private.live.template.json): template for the uncommitted live secret config containing exchange keys and API/UI credentials.

## Docs

- [docs/research-workflow.md](/E:/Code Repo/PricePilot AI/docs/research-workflow.md): research and validation workflow for data download, backtesting, hyperopt, bias checks, and dry-run review.
- [docs/git-workflow.md](/E:/Code Repo/PricePilot AI/docs/git-workflow.md): fixed branch policy for `dev` and `main`, including daily development, release, and hotfix flow.
- [docs/repository-files.md](/E:/Code Repo/PricePilot AI/docs/repository-files.md): file-level reference for the entire tracked repository.

## Runbooks

- [docs/runbooks/deployment-checklist.md](/E:/Code Repo/PricePilot AI/docs/runbooks/deployment-checklist.md): pre-dry-run and pre-live checklist, plus go-live sequence.
- [docs/runbooks/incident-response.md](/E:/Code Repo/PricePilot AI/docs/runbooks/incident-response.md): incident handling steps for key exposure, order failures, time drift, and stoploss cascades.

## Infrastructure

- [infra/.env.example](/E:/Code Repo/PricePilot AI/infra/.env.example): environment variable example for Docker Compose execution.
- [infra/docker-compose.yml](/E:/Code Repo/PricePilot AI/infra/docker-compose.yml): Docker Compose definition for dry-run and live Freqtrade services.

## Reports

- [reports/backtests/.gitkeep](/E:/Code Repo/PricePilot AI/reports/backtests/.gitkeep): keeps the committed backtest report directory present in the repository.
- [reports/daily/.gitkeep](/E:/Code Repo/PricePilot AI/reports/daily/.gitkeep): keeps the committed daily report directory present in the repository.
- [reports/hyperopt/.gitkeep](/E:/Code Repo/PricePilot AI/reports/hyperopt/.gitkeep): keeps the committed hyperopt report directory present in the repository.

## Scripts

- [scripts/bootstrap.ps1](/E:/Code Repo/PricePilot AI/scripts/bootstrap.ps1): creates local runtime directories and pulls the Freqtrade Docker image.
- [scripts/download_data.ps1](/E:/Code Repo/PricePilot AI/scripts/download_data.ps1): downloads historical market data for the configured Binance Spot pairs and timeframes.
- [scripts/run_backtest.ps1](/E:/Code Repo/PricePilot AI/scripts/run_backtest.ps1): runs Freqtrade backtesting and writes raw and rendered backtest reports.
- [scripts/run_hyperopt.ps1](/E:/Code Repo/PricePilot AI/scripts/run_hyperopt.ps1): runs constrained hyperparameter optimization and writes hyperopt reports.
- [scripts/validate_strategy.ps1](/E:/Code Repo/PricePilot AI/scripts/validate_strategy.ps1): runs backtest validation, lookahead-analysis, and recursive-analysis.
- [scripts/run_research_cycle.ps1](/E:/Code Repo/PricePilot AI/scripts/run_research_cycle.ps1): orchestrates the full research flow from data download through validation.
- [scripts/run_dry.ps1](/E:/Code Repo/PricePilot AI/scripts/run_dry.ps1): starts the dry-run trading service with Docker Compose.
- [scripts/run_live.ps1](/E:/Code Repo/PricePilot AI/scripts/run_live.ps1): starts the live trading service after checking that the private live config exists.
- [scripts/daily_report.ps1](/E:/Code Repo/PricePilot AI/scripts/daily_report.ps1): generates markdown and JSON daily reports from the dry-run or live trade database.
- [scripts/backup_db.ps1](/E:/Code Repo/PricePilot AI/scripts/backup_db.ps1): backs up SQLite trade databases and the active JSON configs into a timestamped folder.
- [scripts/render_backtest_report.py](/E:/Code Repo/PricePilot AI/scripts/render_backtest_report.py): converts raw backtest console output into a markdown summary and captures recent artifacts.
- [scripts/render_hyperopt_report.py](/E:/Code Repo/PricePilot AI/scripts/render_hyperopt_report.py): converts raw hyperopt output into a markdown summary and extracts simple JSON snapshots.
- [scripts/render_daily_report.py](/E:/Code Repo/PricePilot AI/scripts/render_daily_report.py): reads the Freqtrade SQLite database and renders daily JSON and markdown summaries.

## User Data

- [user_data/backtest_results/.gitkeep](/E:/Code Repo/PricePilot AI/user_data/backtest_results/.gitkeep): keeps the backtest artifact directory present in the repository.
- [user_data/hyperopt_results/.gitkeep](/E:/Code Repo/PricePilot AI/user_data/hyperopt_results/.gitkeep): keeps the hyperopt artifact directory present in the repository.
- [user_data/logs/.gitkeep](/E:/Code Repo/PricePilot AI/user_data/logs/.gitkeep): keeps the runtime log directory present in the repository.

## Strategies

- [user_data/strategies/BinanceSpotLowFrequencyStrategy.py](/E:/Code Repo/PricePilot AI/user_data/strategies/BinanceSpotLowFrequencyStrategy.py): primary low-frequency Binance Spot strategy with multi-timeframe trend filters, BTC market guard, protections, hyperopt parameters, dynamic stake sizing, and custom exits.
- [user_data/strategies/SimpleSpotStrategy.py](/E:/Code Repo/PricePilot AI/user_data/strategies/SimpleSpotStrategy.py): earlier baseline example strategy retained as a simple reference implementation.

## Local-Only Directories

- `.venv/`: local Python virtual environment for helper scripts. This is ignored and should not be committed.
- `.idea/`: IDE project metadata. This is ignored and should not be committed.
- `user_data/data/`: downloaded market data cache. This is ignored because it is generated locally and can be very large.
- `user_data/*.sqlite`: dry-run and live trade databases. These are ignored because they are runtime state.
- `reports/backtests/*`, `reports/hyperopt/*`, `reports/daily/*`: generated research and operations reports. Only the directory placeholders are tracked.
- `config/private.live.json`: live secret configuration. This must remain local and uncommitted.
