# 运行指南（Runbook）

本仓库以 SSD（Spec-Driven Development）组织交易系统。实现需严格依规格执行。

## 目录速览
- 规格：`specs/`（单一事实来源）
- 配置：`config/params.yaml`
- 工作流：`workflows/spec-workflow-mcp.yaml`
- 复盘：`reviews/`
- 日志：`logs/`

## 生命周期（对应 workflows/spec-workflow-mcp.yaml）
1) validate-specs：校验规格与参数引用是否完整
2) data-ingest：拉取并标准化 D/H4/H1 的 OHLCV
3) signal-generation：按 `2-*.yml` 与 `3-resonance.yml` 生成事件
4) execution-simulation：按 `4-entry/5-risk/6-position-sizing/8-exit` 回放
5) review-export：输出 `reviews/daily.md`，可对接 Notion

## 参数
统一在 `config/params.yaml` 调整（如 ADX 阈值、DMI gap、超趋势参数、风险/仓位/离场）。

## 与 MCP 对接
- 启用 `workflows/spec-workflow-mcp.yaml` 中 `integrations.notion.enabled: true`
- 准备 MCP 适配器（外部）：
  - 将 `artifacts/trades.ndjson`、`artifacts/events.ndjson` 汇总为复盘内容
  - 推送到 Notion 数据库（字段映射见 `specs/9-logging-and-review.yml`）

## 实现建议（参考）
- 语言/栈自选（Python/Rust/TS）。关键是模块边界与事件模式：
  - 指标引擎：输出标准化 `STRENGTH_OK/WEAK`、`DIRECTION_BULLISH_FLIP`、`MOMENTUM_*`
  - 共振器：窗口去重后产出 `STRONG_UPTREND_START`
  - 执行器：`ENTRY_LONG`（含 entry/stop）、风控校验、仓位计算、离场事件
  - 事件总线：NDJSON 追加写，字段包含 rule_id、params 快照与证据引用

## 最小验收
- 在任意数据集上，流水线至少产出：`artifacts/events.ndjson`、`artifacts/trades.ndjson`、`reviews/daily.md`
- 所有 `ENTRY_LONG` 都有 `initial_stop` 与 `POSITION_SIZED` 