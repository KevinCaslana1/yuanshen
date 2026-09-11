# Handoff

> 本文件保持很短，只服务于新会话、上下文压缩或其他 Agent 的快速接管。

## 当前做到哪里

已完成 PRE-MODELING GATE、全部 Q1 Gate 和 Q1 表面 signed-error 数值审计。Q1 已完成人工冻结：candidate `deliverables/candidate/result1.xlsx` 已按 COPY ONLY 规则复制到 `deliverables/final/result1.xlsx`，最终工作簿、清单、审计和图表包均通过验证；本轮未重生成或修改 final。Q2 已完成设计与契约草案，但 solver/result2 尚未开始；Q3/Q4 仍为 NOT STARTED，三者按用户要求暂停。

## 刚刚完成什么

已冻结 Python/依赖和 Q1 交付契约；完成 `EXP-Q1-SURFACE-DECAY` signed/absolute 对照、0–60 s 边界/求解轨迹、EXP-003 时间收敛和 EXP-004 空间收敛。r=1.9 cm 在 35–36 s 穿零，归类 `pointwise error zero-crossing / cancellation dip`；Q1 final 未改动。Q2 的设计资料仍在，但本轮不运行 Q2 solver。

## 当前最好结果

生产候选为边界聚类保守径向 FVM + BE 首步/BDF2 + Picard：base320、实际 338 个径向控制体、`dt=.25 s`、0–1800 s 全时段、21 个官方位置。全时段综合估计数值不确定度最大为温度 `1.4012175e-6 °C`、水分 `2.7414225e-5 kg/kg`，均严格小于 `5e-5`。候选已通过格式、有限值、轴线、随机 20 单元和纸面表格追溯验证；舍入歧义仅作为辅助诊断，不构成自动失败。

## 当前主要决策

`A题/` 是 OFFICIAL_SOURCE / IMMUTABLE_SOURCE。正式结果只能从官方模板复制到 `deliverables/candidate/` 后生成。

Q1 早期表面深谷不得作为算法优越性或快速收敛证据；signed error 与 absolute error 必须同时保留。

## 不要重复尝试什么

已记录并修复一次 smoke 入口问题、一次 EXP-003 比较助手问题、一次聚类 BDF2 首步装配分派问题和一次冻结产物时间戳哈希问题；不要把候选工作簿直接放入 `deliverables/final/`，不要修改官方 result 模板，不要把 HYPOTHESIS 写成 FINDING，不要在未获 implementation authorization 前启动 Q2 solver。

## 下一步

Q1 人工冻结已批准并执行。接管时优先阅读 `experiments/EXP-Q1-SURFACE-DECAY/metrics.json`、`experiments/EXP-Q1-SURFACE-DECAY/surface_signed_error_15_45s.csv`、`experiments/EXP-003/metrics.json`、`experiments/EXP-004/metrics.json`，再阅读 `docs/Q1_FINAL_FREEZE_AUDIT.md`；下一步等待用户是否继续论文整理或恢复 Q2，不得自动生成 `result2.xlsx` 或启动 Q3/Q4。

## 重点阅读文件

`AGENTS.md`、`docs/PROBLEM_SPEC.md`、`docs/DATA_CATALOG.md`、`docs/STATE.md`、`docs/TODO.md`、`docs/RUNBOOK.md`、`docs/VALIDATION.md`。

## 风险与注意事项

官方资产位于 `A题/`，必须保持只读。Q1 final 已写入并锁定；B0 必须保留为 Baseline；Q2 终点/环境/界面平均/精度门仍需人工确认；Q4 动态半径问题仍只阻塞 Q4 MODEL IMPLEMENTATION。仓库为 Public，CI 未作为 Gate 依赖；本轮只做本地提交，不推送远端。
