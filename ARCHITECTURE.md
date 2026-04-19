# PricePilot AI Architecture

## 1. Scope

This project should be built around `Freqtrade` as the trading engine, not as a thin inspiration source.

Recommended V1 scope:

- Exchange: `Binance Spot`
- Framework: `Freqtrade stable`
- Runtime modes: `backtest -> dry-run -> live`
- Strategy class: one simple trend-following or mean-reversion strategy
- Risk model: fixed fractional stake, hard stoploss, exchange-side stoploss, protections
- Deployment target: single private host or VPS

Explicit non-goals for V1:

- No futures
- No leverage
- No martingale / grid averaging
- No multi-exchange routing
- No self-built order engine replacing Freqtrade internals
- No promise of profitability

## 2. Key Constraints

As of `2026-04-19`, the Freqtrade stable docs indicate:

- Freqtrade supports `Binance` for both `spot` and `futures`
- For `Binance spot`, stoploss on exchange is supported via `stop-loss-limit`
- Freqtrade recommends starting in `dry-run`
- Freqtrade provides `lookahead-analysis` and `recursive-analysis` to validate strategy correctness
- Freqtrade REST API should not be exposed to the public internet

Binance Spot API docs indicate:

- Secure endpoints require signed requests
- API keys and secrets are sensitive
- API keys can be permission-scoped
- A key does not have `TRADE` permission by default

Geo / account note:

- Freqtrade stable exchange notes currently state that `binance.com` has geo restrictions including the `United States`
- If the trading account is on `binance.us`, the exchange id must be `binanceus`, not `binance`

## 3. Architecture Principle

Use Freqtrade for:

- market data access
- strategy execution loop
- backtesting
- hyperopt
- exchange integration through CCXT
- position persistence
- bot control via REST / FreqUI

Build custom project code only around:

- strategy code
- config layering
- deployment automation
- safety controls
- monitoring and reporting
- research workflow orchestration

Do not re-implement:

- order placement
- wallet syncing
- exchange adapters
- backtest engine

## 4. High-Level System

```text
+---------------------------+
| Research / Validation     |
| download-data             |
| backtesting               |
| hyperopt                  |
| lookahead-analysis        |
| recursive-analysis        |
+-------------+-------------+
              |
              v
+---------------------------+
| Strategy Registry         |
| strategies/*.py           |
| versioned configs         |
| approved parameter sets   |
+-------------+-------------+
              |
              v
+---------------------------+
| Freqtrade Runtime         |
| trade loop                |
| DB persistence            |
| protections               |
| stoploss handling         |
+------+------+-------------+
       |      |
       |      +-------------------+
       |                          |
       v                          v
+-------------+         +------------------+
| Binance API |         | REST / FreqUI    |
| market/order|         | localhost only   |
+-------------+         +------------------+
              |
              v
+---------------------------+
| Observability             |
| logs                      |
| trade DB                  |
| daily reports             |
| alerts                    |
+---------------------------+
```

## 5. Recommended Repo Structure

```text
/ARCHITECTURE.md
/docs/
  /runbooks/
    incident-response.md
    deployment-checklist.md
/infra/
  docker-compose.yml
  .env.example
/config/
  base.spot.json
  dryrun.json
  live.json
  private.live.template.json
/user_data/
  /strategies/
    SimpleSpotStrategy.py
  /data/
  /backtest_results/
  /hyperopt_results/
/scripts/
  bootstrap.ps1
  download_data.ps1
  validate_strategy.ps1
  run_dry.ps1
  run_live.ps1
  backup_db.ps1
```

## 6. Runtime Layers

### 6.1 Research Layer

Purpose:

- download historical candles
- iterate on strategy logic
- backtest and compare variants
- run parameter search
- reject biased strategies before deployment

Core commands:

- `freqtrade download-data`
- `freqtrade backtesting`
- `freqtrade hyperopt`
- `freqtrade lookahead-analysis`
- `freqtrade recursive-analysis`

Research gate before dry-run:

1. Backtest on in-sample data
2. Backtest on out-of-sample data
3. Run lookahead analysis
4. Run recursive analysis
5. Review drawdown, trade count, expectancy, profit factor
6. Approve only if the strategy survives all checks

### 6.2 Strategy Layer

One strategy class per executable idea.

Recommended V1 strategy characteristics:

- spot only
- long only
- timeframe `5m` or `15m`
- 5 to 15 liquid USDT pairs
- fixed `startup_candle_count` sized from recursive-analysis results
- vectorized pandas logic only
- no `iloc[-1]` decision logic in populate methods

Strategy responsibilities:

- indicator generation
- entry signal generation
- exit signal generation
- optional custom stake sizing
- optional custom stoploss
- protections property

Strategy should not:

- read raw secrets
- make direct Binance API calls
- manage external state outside documented callbacks

### 6.3 Execution Layer

Execution is a standard Freqtrade bot instance.

Responsibilities:

- fetch candles
- compute signals
- place and manage orders
- persist trades to DB
- expose local API / UI
- enforce order and stoploss behavior

Recommended operating modes:

- `dev`: backtesting only
- `paper`: dry-run with simulated wallet
- `prod`: live trading with real funds

### 6.4 Control Layer

Lightweight project-owned wrapper around Freqtrade.

Responsibilities:

- config assembly
- environment separation
- startup scripts
- deployment checklists
- backups
- daily summary generation

This layer should stay thin. Avoid creating an additional application server unless there is a hard requirement.

### 6.5 Observability Layer

Minimum:

- Freqtrade logs
- SQLite trade DB for V1
- daily PnL report
- alerting on bot stopped / repeated stoploss / API failure

Preferred V2 upgrade:

- Postgres
- Prometheus exporter
- Grafana dashboards
- structured log shipping

## 7. Configuration Design

Use config layering.

### 7.1 Base config

Contains:

- exchange-independent runtime defaults
- pairlist
- stake sizing rules
- protections
- order types
- API server localhost binding

### 7.2 Dry-run config

Overrides:

- `dry_run: true`
- dry-run DB path
- simulated wallet size
- fake or empty exchange credentials

### 7.3 Live config

Overrides:

- `dry_run: false`
- live DB path
- strict capital limits
- production pairlist

### 7.4 Private secrets config

Contains only:

- API key
- API secret
- optional exchange password if ever needed

Must never be committed.

This follows Freqtrade guidance to keep secrets in a separate config file loaded in addition to the base config.

## 8. Security Model

### 8.1 API Key Design

For V1 live trading:

- create one dedicated Binance API key for this bot only
- enable only required permissions
- whitelist the server IP if Binance account policy allows it
- do not reuse personal/manual trading keys

Important nuance:

- Freqtrade live trading needs account and order access, so the live key must support the permissions required for live trade execution and order/account monitoring
- dry-run does not need real trading credentials

### 8.2 Secret Handling

Store secrets in one of:

- uncommitted private config file
- environment variables injected at runtime

Never store secrets in:

- strategy files
- scripts
- committed JSON files
- logs

### 8.3 REST / UI Security

The REST API and FreqUI should:

- listen on `127.0.0.1`
- use a strong unique username and password
- use a strong `jwt_secret_key`
- use a random `ws_token`
- not be exposed directly to the internet

If remote access is required, put it behind:

- VPN, or
- SSH tunnel, or
- reverse proxy with allowlist and authentication

Do not bind the bot directly to public `0.0.0.0` unless there is a controlled private network boundary.

### 8.4 Host Security

Production host controls:

- dedicated non-admin OS user
- disk encryption if possible
- firewall default deny inbound
- automatic security updates
- NTP time sync enabled
- backups for DB and configs

## 9. Trading Risk Model

This is the most important non-functional requirement.

### 9.1 V1 Capital Rules

Recommended defaults:

- stake currency: `USDT`
- max open trades: `3`
- per-trade stake: `2%` to `5%` of deployable capital
- capital reserve: keep `20%` to `40%` unallocated
- pair universe: only liquid spot pairs

### 9.2 Hard Risk Controls

Enable:

- static initial stoploss
- `stoploss_on_exchange`
- emergency exit order type
- cooldown protection
- stoploss guard
- max drawdown protection

For Binance Spot specifically:

- use exchange-side stoploss because Freqtrade supports it on Binance spot

### 9.3 Pair Controls

Use:

- static or tightly filtered volume-based pairlist
- quote currency restricted to `USDT`
- blacklist low-quality or operationally risky pairs

If Binance fee discounts are paid in BNB:

- blacklist `BNB/USDT` or the equivalent stake pair to avoid operational conflicts noted in Freqtrade docs

### 9.4 Forbidden V1 Behaviors

- no averaging down
- no unlimited re-entries
- no leverage
- no manual intervention that bypasses the bot without runbook steps

## 10. Order Handling Design

V1 recommendation:

- spot only
- start with limit entry and limit exit if fills are reliable
- use exchange stoploss
- prefer conservative slippage assumptions in backtests

Operational rule:

- backtest order assumptions must stay close to live configuration

If live fills diverge materially from backtests:

- reduce pair universe
- widen liquidity filters
- simplify entry logic
- consider market exits for emergency paths only

## 11. Data Flow

### 11.1 Historical Data

Source:

- Freqtrade `download-data`

Storage:

- `user_data/data/<exchange>/...`

Use:

- backtesting
- hyperopt
- bias validation

### 11.2 Runtime Market Data

Source:

- Binance via Freqtrade / CCXT

Use:

- candle updates
- pricing
- order state updates

### 11.3 Trade State

Source of truth:

- Freqtrade DB

Contains:

- trade lifecycle
- order lifecycle
- realized results
- open positions

## 12. Database Strategy

V1:

- SQLite is acceptable
- keep separate DB files for `dry-run` and `live`

V2:

- migrate live trading to Postgres for better durability, backups, and inspection

Never:

- share one DB between dry-run and live
- reset live DB casually

## 13. Validation Pipeline

This pipeline is mandatory before any live deployment.

1. Implement strategy
2. Download enough history
3. Backtest on development range
4. Backtest on holdout range
5. Run `lookahead-analysis`
6. Run `recursive-analysis`
7. Run hyperopt carefully, then re-backtest without optimization leakage
8. Run dry-run for at least `2 to 4 weeks`
9. Compare dry-run fills and backtest assumptions
10. Approve for tiny-capital live deployment

Approval criteria should include:

- no lookahead bias
- acceptable indicator variance
- controlled drawdown
- sufficient trade count
- no unstable bot behavior
- no repeated exchange/API failures

## 14. Deployment Topology

### Option A: Single-host V1

Recommended.

Components:

- one bot container or process
- one local DB
- one local FreqUI / REST endpoint
- one scheduled backup task

Advantages:

- simplest
- easiest to reason about
- lowest operational risk

### Option B: Split research and production hosts

Recommended V2.

Research host:

- backtests
- hyperopt
- report generation

Production host:

- dry/live bot only

Advantages:

- isolation of credentials
- lower operational blast radius
- cleaner resource usage

## 15. Operational Runbooks

You should maintain explicit runbooks for:

- starting dry-run
- promoting dry-run config to live
- rotating Binance API keys
- handling stoploss cascade
- handling repeated order rejections
- handling API desync / time drift
- restoring from DB backup
- disabling the bot safely

## 16. Recommended V1 Defaults

These are intentionally conservative.

- Exchange: `binance`
- Market: `spot`
- Quote: `USDT`
- Pairs: `BTC/USDT`, `ETH/USDT`, `SOL/USDT`, `XRP/USDT`, `BNB/USDT` excluded if using BNB fee discount
- Timeframe: `15m`
- Max open trades: `3`
- Stake mode: fixed or small unlimited with hard cap
- Stoploss: `-0.08` to `-0.12` initial research range
- Protections: `CooldownPeriod`, `StoplossGuard`, `MaxDrawdown`
- Dry-run duration before live: minimum `14 days`, preferably `28 days`
- First live capital: amount you can fully afford to lose

## 17. Professional Delivery Roadmap

### Phase 1

- initialize Freqtrade project
- create base configs
- implement one simple spot strategy
- run data download and backtests

### Phase 2

- bias validation
- recursive validation
- dry-run environment
- logs and daily reporting

### Phase 3

- limited live trading
- operational runbooks
- backups and alerting

### Phase 4

- strategy portfolio
- Postgres
- dashboarding
- separate research/prod nodes

## 18. What "Accurate" Means Here

In quantitative trading, "accurate" architecture does not mean guaranteed profit.

It means:

- strategy logic is reproducible
- backtest and runtime assumptions are aligned
- known bias classes are checked
- exchange-specific constraints are respected
- secrets and operational access are controlled
- loss is bounded by design

No architecture can make trading outcomes completely certain.

## 19. Recommended Build Decision

The correct V1 build is:

- `Freqtrade stable`
- `Binance Spot`
- `single-host`
- `dry-run first`
- `one simple strategy`
- `exchange-side stoploss`
- `strict protections`
- `separate private config for secrets`

That is the safest professional baseline.

## 20. References

- Freqtrade home: https://www.freqtrade.io/en/stable/
- Freqtrade exchange notes: https://www.freqtrade.io/en/stable/exchanges/
- Freqtrade strategy customization: https://www.freqtrade.io/en/stable/strategy-customization/
- Freqtrade basics: https://www.freqtrade.io/en/stable/bot-basics/
- Freqtrade data download: https://www.freqtrade.io/en/stable/data-download/
- Freqtrade backtesting: https://docs.freqtrade.io/en/stable/backtesting/
- Freqtrade hyperopt: https://www.freqtrade.io/en/stable/hyperopt/
- Freqtrade lookahead analysis: https://www.freqtrade.io/en/stable/lookahead-analysis/
- Freqtrade recursive analysis: https://www.freqtrade.io/en/stable/recursive-analysis/
- Freqtrade stoploss: https://www.freqtrade.io/en/stable/stoploss/
- Freqtrade strategy callbacks: https://www.freqtrade.io/en/stable/strategy-callbacks/
- Freqtrade REST API: https://www.freqtrade.io/en/stable/rest-api/
- Binance Spot API docs: https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md
