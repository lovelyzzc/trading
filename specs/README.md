# SSD 规格索引（Spec Index）

> 本目录为个人交易系统的“单一事实来源”（SSoT）。任何实现均需以此为准。

- 基础与术语：`0-glossary.md`
- 系统级目标与约束：`1-system.md`
- 信号层规格：
	- 趋势强度 ADX：`2-strength.adx.yml`
	- 趋势方向 ML Adaptive SuperTrend：`2-direction.ml_supertrend.yml`
	- 趋势动能 DMI：`2-momentum.dmi.yml`
- 共振与决策：`3-resonance.yml`
- 入场（回调/突破）：`4-entry.yml`
- 风险控制：`5-risk.yml`
- 仓位管理：`6-position-sizing.yml`
- 多时间框架：`7-timeframes.yml`
- 离场与持盈：`8-exit.yml`
- 记录与复盘：`9-logging-and-review.yml`

实现须满足：
- 规格可配置（`/config/params.yaml`）
- 可追踪（所有输出含来源与参数快照）
- 可复现（固定数据源与版本，记录随机种子）
- 可验证（每个规格含验收标准/示例） 