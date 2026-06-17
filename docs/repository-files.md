# Repository Files

## 核心文档

- `GOAL.md`：已确认目标、严格价格行为定义和安全边界。
- `README.md`：项目入口、运行方式、实验结果和作业交付说明。
- `ARCHITECTURE.md`：观察、Agent、风险门禁和执行架构。
- `docs/assignment-report.md`：中文人工智能实践项目报告。
- `reports/course-project-report.md`：课程项目详细报告的提交与查看入口。
- `docs/research-workflow.md`：测试、消融、Freqtrade 和 Testnet 验证流程。

## 严格价格行为策略

- `user_data/strategies/price_action_core.py`：摆动点、结构、BOS/CHoCH、流动性扫荡、蜡烛确认和结构化交易计划。
- `user_data/strategies/BinanceSpotLowFrequencyStrategy.py`：严格价格行为 Freqtrade 主策略。
- `user_data/strategies/SimpleSpotStrategy.py`：保留的传统指标基线，不属于严格价格行为主策略。

## Agent 与执行

- `scripts/agent_advisor.py`：确定性 Advisor、基础模型 Agent 和风险门禁。
- `scripts/price_action_agent.py`：分析、决策 ID、重复执行拦截与订单流程。
- `scripts/binance_testnet_client.py`：Binance Spot Testnet REST 客户端。
- `scripts/run_price_action_agent.ps1`：Agent PowerShell 入口。
- `scripts/evaluate_model_agent.py`：批量比较基础模型 Agent 与确定性 Advisor。
- `scripts/evaluate_model_agent.ps1`：基础模型评测 PowerShell 入口。
- `docs/runbooks/binance-testnet-simulation.md`：Testnet 运行手册。

## 实验与测试

- `scripts/run_price_action_experiment.py`：独立走步模拟和消融实验。
- `scripts/run_price_action_experiment.ps1`：实验 PowerShell 入口。
- `tests/`：标准库自动化测试。
- `reports/experiments/`：生成的消融实验结果。

## Freqtrade 工作流

- `config/`：基础、Dry-run、Live 和私有配置模板。
- `infra/docker-compose.yml`：Dry-run 与 Live 容器定义。
- `scripts/download_data.ps1`：下载历史数据。
- `scripts/run_backtest.ps1`：运行回测并生成报告。
- `scripts/run_hyperopt.ps1`：受约束参数优化。
- `scripts/validate_strategy.ps1`：回测、lookahead 和 recursive analysis。
- `scripts/run_dry.ps1`：启动 Dry-run。

## 作业交付

- `scripts/package_assignment.ps1`：生成作业压缩包，排除私有配置、密钥、执行账本和缓存。
- `reports/backtests/`：Freqtrade 回测报告。
- `reports/agent/`：Agent 分析报告。
- `reports/experiments/`：消融实验结果。
