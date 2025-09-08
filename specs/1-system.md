# 系统级规格（System Spec）

## 目标
- 在强单边上涨趋势中，以小亏损捕获大波段，实现正期望值。
- 平均持仓：数天至数周。主要捕获日线主升段。

## 非功能性约束
- 可配置、可追踪、可复现、可验证。
- 数据可追溯（数据源、时间框、时区、采样方法）。
- 日志标准化（结构化事件流）。

## 依赖与输入
- 数据：OHLCV（至少日线、H4/H1），统一时区。
- 指标：ADX、DMI、ML Adaptive SuperTrend（实现可替换，接口固定）。

## 架构映射
- 信号层：`2-strength.adx.yml`、`2-direction.ml_supertrend.yml`、`2-momentum.dmi.yml`
- 共振层：`3-resonance.yml`
- 执行层：`4-entry.yml`、`8-exit.yml`
- 风控层：`5-risk.yml`、`6-position-sizing.yml`
- 时框编排：`7-timeframes.yml`
- 记录复盘：`9-logging-and-review.yml`

## 系统级输出
- 事件：`STRONG_UPTREND_START`、`ENTRY_LONG`、`ADJUST_STOP`、`EXIT_LONG`、`REVIEW_ITEM`
- 事件均需附带：触发规则ID、参数快照、上/下游证据引用、时间框与时间戳。

## 验收标准（高层）
- 当 S1/D1/M1/M2 共振时，发出唯一的 `STRONG_UPTREND_START` 事件，不得重复抖动。
- 入场事件必须携带可执行的 `entry_price`、`initial_stop` 与 `risk_amount`。
- 任一离场事件能完整追溯其触发依据（如 SuperTrend 翻转）。 