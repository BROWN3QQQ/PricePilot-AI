# PricePilot AI 研究与验证流程

## 目标

验证严格价格行为策略是否可复现、是否存在未来数据问题，以及 Agent 和风险门禁是否遵守安全边界。

## 建议顺序

### 1. 自动化测试

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### 2. 独立走步与消融实验

```powershell
.\scripts\run_price_action_experiment.ps1
```

该实验比较完整价格行为策略、结构突破、蜡烛形态和移除风险门禁等变体。结果写入 `reports/experiments`。

### 3. Freqtrade 历史数据

```powershell
.\scripts\download_data.ps1 -Timerange 20230101-
```

### 4. Freqtrade 回测

```powershell
.\scripts\run_backtest.ps1 -Timerange 20230101-
```

### 5. 偏差验证

```powershell
.\scripts\validate_strategy.ps1 -Timerange 20230101-
```

必须检查：

- lookahead-analysis
- recursive-analysis
- 样本内与样本外表现
- 手续费和滑点敏感性
- 交易数量、最大回撤、Profit Factor 和 Expectancy

### 6. Agent 分析与 Testnet

```powershell
.\scripts\run_price_action_agent.ps1 -AdvisorMode heuristic
```

配置模型后：

```powershell
.\scripts\run_price_action_agent.ps1 -AdvisorMode model
.\scripts\evaluate_model_agent.ps1 -Symbol BTCUSDT -MaxSamples 20
```

只有在风险门禁批准后才验证 Testnet test-order：

```powershell
.\scripts\run_price_action_agent.ps1 -SubmitTestnetOrder
```

## 研究规则

- 不因单一交易对或单一时间段盈利就宣称策略有效。
- 不只报告胜率。
- 不对同一份样本反复调参后将结果当作样本外表现。
- 模型 Advisor 与确定性 Advisor 应分别记录。
- 模型输出不能改变结构失效位、最大损失或重复执行门禁。
- 正式进入 Dry-run 前必须通过 lookahead 与 recursive analysis。
