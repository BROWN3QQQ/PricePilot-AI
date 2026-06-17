# PricePilot AI Architecture

## 1. Design Principle

PricePilot AI separates observation, advice, approval, and execution.

The executable strategy is strict price action. A base-model Agent is an advisory reviewer, not an unrestricted trader. Every buy must pass deterministic checks after Agent output.

## 2. System Flow

```text
Binance OHLCV
    |
    v
Strict Price-Action Engine
swings -> structure -> BOS/CHoCH -> sweeps -> candle confirmation
    |
    v
Deterministic Candidate
action + setup + entry + invalidation + target + risk/reward
    |
    v
Base-Model Agent
accept / explain / veto
    |
    v
Deterministic Risk Gate
confidence + setup match + risk + structural loss + duplicate decision
    |
    +----------------------+
    |                      |
    v                      v
Blocked Report       Binance Spot Testnet Order
                           |
                           v
                    lookup + execution ledger
```

## 3. Strict Price-Action Engine

`user_data/strategies/price_action_core.py` provides two compatible interfaces:

- `compute_price_action_indicators`: vectorized Freqtrade DataFrame features.
- `analyze_candles`: standalone Agent and experiment analysis.

The engine detects:

- confirmed swing highs and lows without future-data access
- bullish, bearish, or range structure
- break of structure and change of character
- bullish and bearish liquidity sweeps
- rejection and engulfing candles
- breakout retests
- structural invalidation and target prices
- price-action buy, sell, and risk scores

True range and volume are used only as risk and participation context. They do not replace price-action decisions.

## 4. Agent Contract

`scripts/agent_advisor.py` supports:

- `heuristic`: deterministic and reproducible policy
- `model`: OpenAI-compatible chat-completion endpoint
- `auto`: use the model when configured, otherwise use the heuristic policy

The model receives only structured price-action evidence. It may veto a candidate, but it cannot create a buy when the deterministic policy returned `HOLD` or `EXIT`.

## 5. Risk Gate

The risk gate verifies:

- Agent action is `BUY`
- deterministic recommendation is `BUY`
- observed and selected setups match
- setup is allowlisted
- confidence and risk thresholds pass
- no bearish sweep or support breakdown is present
- structural entry, invalidation, and target prices are valid
- minimum risk/reward is met
- quote amount respects exposure and maximum-loss limits

Quote sizing is capped by:

```text
max_loss_amount / structural_stop_distance_pct
```

## 6. Execution Safety

`scripts/price_action_agent.py` defaults to analysis only.

When Testnet order submission is requested:

- a stable decision ID is generated from the candle and structural plan
- the ID becomes a Binance client order ID
- the local execution ledger blocks repeated submission of the same decision and mode
- a real Testnet order is looked up after submission
- credentials are read only from environment variables

## 7. Validation Layers

1. Standard-library unit tests.
2. Standalone walk-forward and ablation experiments.
3. Freqtrade backtesting.
4. Freqtrade lookahead analysis.
5. Freqtrade recursive analysis.
6. Freqtrade Dry-run.
7. Binance Spot Testnet order validation and simulated execution.

The standalone experiment is intentionally conservative: fees and slippage are included, and a candle that touches stop and target is counted as a stop first.

## 8. Safety Boundary

- Spot and long-only.
- No real funds in the assignment workflow.
- No leverage, futures, martingale, grid averaging, or unlimited re-entry.
- No Agent-controlled direct order placement.
- No claim of profitability.
