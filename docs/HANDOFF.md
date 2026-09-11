# Handoff

> 本文件保持很短，只服务于新会话、上下文压缩或其他 Agent 的快速接管。

## 当前做到哪里

已完成 PRE-MODELING GATE、Q1 MODEL DESIGN GATE、Q1 IMPLEMENTATION & NUMERICAL VALIDATION GATE 和 Q1 NUMERICAL CONVERGENCE DIAGNOSIS & REMEDIATION GATE；当前进入 Q1 INITIAL-LAYER & SURFACE-ACCURACY GATE。初始水分层诊断获支持，边界聚类为短时数值候选，但最终全时段精度门仍阻塞。Q2/Q3/Q4 仍为 NOT STARTED。

## 刚刚完成什么

已冻结 Python/依赖和 Q1 交付契约；OQ-005/OQ-006/OQ-007/OQ-008 已登记决策。完成 M1/M2/B0/M3 对照、EXP-001–EXP-007、最终精度初审、制造解 benchmark、误差诊断、Picard 敏感性、BDF2 启动对照、表面衰减、聚类 benchmark/短时对照/时间梯。新增非均匀保守 FVM 和全 21 个官方位置的舍入认证；未生成任何结果工作簿。

## 当前最好结果

独立 benchmark 支持均匀和边界聚类保守 FVM 的近二阶空间阶、BE 近一阶时间阶；真实 Q1 聚类 base1280、`dt=.0078125 s` 的 t=1 s 表面参考为 `2.5177587784 kg/kg`，保守时间剩余 `3.1850e-5 kg/kg`、空间剩余 `1.2259e-6 kg/kg`，21 个官方位置中 20 个舍入认证、表面 1 个歧义。早期 BDF2 子步未显示改善。这些不是论文最终结论，且尚未生成 `result1.xlsx`。

## 当前主要决策

`A题/` 是 OFFICIAL_SOURCE / IMMUTABLE_SOURCE。正式结果只能从官方模板复制到 `deliverables/candidate/` 后生成。

## 不要重复尝试什么

已记录并修复一次 smoke 入口问题和一次 EXP-003 比较助手问题；不要把内部实验直接写成论文结论，不要生成 `result1.xlsx`，不要修改官方 result 模板，不要把 HYPOTHESIS 写成 FINDING。

## 下一步

等待人工审查 `docs/Q1_INITIAL_LAYER_AUDIT.md`，决定是否批准边界聚类候选及固定生产时间策略的 0–1800 s 全网格复验；在最终门通过和人工确认前不得生成 candidate `result1.xlsx`、进入 freeze run 或启动 Q2/Q3/Q4。

## 重点阅读文件

`AGENTS.md`、`docs/PROBLEM_SPEC.md`、`docs/DATA_CATALOG.md`、`docs/STATE.md`、`docs/TODO.md`、`docs/RUNBOOK.md`、`docs/VALIDATION.md`。

## 风险与注意事项

官方资产位于 `A题/`，必须保持只读。M1/BE 是当前可追溯参考但未通过精度门，边界聚类和 M1-NUM-T2 都只是候选；B0 必须保留为 Baseline。Q4 动态半径问题仍只阻塞 Q4 MODEL IMPLEMENTATION。仓库为 Public，CI 未作为 Gate 依赖；本轮提交 `3b0785a`，按授权不推送远端。
