# PricePilot AI

PricePilot AI 是一个严格价格行为学驱动的 AI Agent 量化交易系统，也是人工智能实践课程作业项目。

它从 Binance OHLCV 原始数据识别摆动结构、BOS/CHoCH、流动性扫荡、拒绝与吞没形态，生成结构化交易计划；基础模型 Agent 只能复核、解释或否决候选；最终由确定性风险门禁决定是否允许 Binance Spot Testnet 模拟买入。

## 核心约束

- 主策略交易信号不使用 EMA、RSI、MACD、ADX、Bollinger Bands 等传统指标。
- 成交量和真实波动范围只作为参与度与风险上下文。
- Agent 不得在价格行为策略未批准时凭空生成买入。
- 默认只分析；自动订单仅面向 Binance Spot Testnet。
- 不使用真实资金、杠杆、期货、马丁格尔或网格加仓。

完整目标见 [GOAL.md](/E:/Code Repo/PricePilot AI/GOAL.md)，架构见 [ARCHITECTURE.md](/E:/Code Repo/PricePilot AI/ARCHITECTURE.md)。

## 系统组成

- `price_action_core.py`：严格价格行为特征、交易计划与独立蜡烛分析。
- `BinanceSpotLowFrequencyStrategy.py`：无传统指标信号的 Freqtrade 策略。
- `agent_advisor.py`：确定性 Advisor 与 OpenAI-compatible 基础模型 Agent。
- `price_action_agent.py`：分析、风险审批、幂等控制与 Testnet 订单流程。
- `binance_testnet_client.py`：行情、账户、订单、查询和取消接口。
- `run_price_action_experiment.py`：走步模拟与消融实验。
- `tests/`：安全边界和核心行为测试。

## 快速验证

### 1. 运行自动化测试

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### 2. 运行价格行为消融实验

默认使用 Binance 公开行情，执行 BTCUSDT 与 ETHUSDT 的 1h 走步模拟：

```powershell
.\scripts\run_price_action_experiment.ps1
```

结果写入 `reports/experiments`。

### 3. 运行 Testnet 分析

默认不会提交订单：

```powershell
.\scripts\run_price_action_agent.ps1 -Symbol BTCUSDT -Interval 1h -AdvisorMode heuristic
```

### 4. 使用基础模型 Agent

配置任意 OpenAI-compatible 接口：

```powershell
$env:PRICEPILOT_LLM_BASE_URL = "https://your-provider.example/v1"
$env:PRICEPILOT_LLM_API_KEY = "your_model_key"
$env:PRICEPILOT_LLM_MODEL = "your_model_name"
.\scripts\run_price_action_agent.ps1 -Symbol BTCUSDT -AdvisorMode model
```

模型只能否决或接受确定性候选，风险门禁始终拥有最终决定权。

批量比较基础模型 Agent 与确定性 Advisor：

```powershell
.\scripts\evaluate_model_agent.ps1 -Symbol BTCUSDT -MaxSamples 20
```

评测会输出行动一致率、模型否决次数、未授权买入尝试和风险门禁通过次数。

### 5. 验证 Testnet 订单

```powershell
$env:BINANCE_TESTNET_API_KEY = "your_testnet_key"
$env:BINANCE_TESTNET_API_SECRET = "your_testnet_secret"
.\scripts\run_price_action_agent.ps1 -SubmitTestnetOrder
```

上面的命令调用 Testnet test-order，不创建实际 Testnet 订单。提交实际 Testnet 模拟订单需要额外指定：

```powershell
.\scripts\run_price_action_agent.ps1 -SubmitTestnetOrder -RealTestnetOrder -Account -OpenOrders
```

同一决策与执行模式会被本地账本拦截，避免重复提交。

## Freqtrade 验证

需要 Docker：

```powershell
.\scripts\bootstrap.ps1
.\scripts\download_data.ps1
.\scripts\run_backtest.ps1
.\scripts\validate_strategy.ps1
.\scripts\run_dry.ps1
```

`validate_strategy.ps1` 会运行回测、lookahead-analysis 与 recursive-analysis。

## 当前实验结果

2026-06-15 使用 Binance 公开行情最近 1000 根 1h 蜡烛进行轻量级走步模拟：

| Symbol | Variant | Trades | Win Rate | Return | Max Drawdown | Profit Factor |
|---|---:|---:|---:|---:|---:|---:|
| BTCUSDT | full_price_action | 3 | 0.00% | -0.56% | 0.56% | 0.00 |
| BTCUSDT | without_risk_gate | 14 | 21.43% | -2.40% | 2.58% | 0.11 |
| ETHUSDT | full_price_action | 5 | 60.00% | 0.27% | 0.33% | 1.80 |
| ETHUSDT | without_risk_gate | 13 | 46.15% | -0.93% | 1.81% | 0.60 |

结果表明风险门禁显著减少交易和回撤，但策略效果存在明显跨资产差异，不构成盈利承诺。完整结果位于 `reports/experiments`。

## 作业交付

详细中文课程项目报告位于：

- [reports/course-project-report.md](/E:/Code Repo/PricePilot AI/reports/course-project-report.md)：提交与查看入口。
- [docs/assignment-report.md](/E:/Code Repo/PricePilot AI/docs/assignment-report.md)：文档目录中的同步副本。

生成最终作业压缩包：

```powershell
.\scripts\package_assignment.ps1
```

压缩包写入 `dist`，并排除密钥、执行账本、缓存和本地私有配置。

## 目录

```text
config/                 Freqtrade 配置
docs/                   报告、工作流和运行手册
infra/                  Docker Compose
reports/experiments/    消融实验结果
scripts/                Agent、实验、报告和运行脚本
tests/                  自动化测试
user_data/strategies/   严格价格行为策略与基线策略
```

## 风险声明

本项目用于研究、课程作业、回测、Dry-run 与 Binance Spot Testnet。量化策略可能亏损，历史或模拟结果不能保证未来表现。
