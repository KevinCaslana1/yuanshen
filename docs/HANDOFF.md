# Handoff

> 本文件保持很短，只服务于新会话、上下文压缩或其他 Agent 的快速接管。

## 当前做到哪里

已完成 PRE-MODELING GATE，并完成 Q1 MODEL DESIGN GATE；Q1 设计已完成，等待人工授权进入实现。Q2/Q3/Q4 仍为 NOT STARTED。

## 刚刚完成什么

已冻结 Python/依赖、Deliverable Contract、Contract Validator、Workflow 测试和官方路径保护。Q1 已完成官方 PDF/附件1/result1 复核、变量单位表、候选模型、Baseline、假设、数值策略、Validation Plan 和 EXP-001–EXP-007 计划。

## 当前最好结果

无真实实验结果。

## 当前主要决策

`A题/` 是 OFFICIAL_SOURCE / IMMUTABLE_SOURCE。正式结果只能从官方模板复制到 `deliverables/candidate/` 后生成。

## 不要重复尝试什么

尚无正式实验失败；不要在实现授权前运行 Q1 正式求解，不要生成 `result1.xlsx`，不要修改官方 result 模板，不要把 HYPOTHESIS 写成 FINDING。

## 下一步

等待人工授权 Q1 实现，并先处理 OQ-005/OQ-006/OQ-007/OQ-008；授权后才能创建最小 `src/q1/` 实现。Q2/Q3/Q4 不得自动启动。

## 重点阅读文件

`AGENTS.md`、`docs/PROBLEM_SPEC.md`、`docs/DATA_CATALOG.md`、`docs/STATE.md`、`docs/TODO.md`、`docs/RUNBOOK.md`、`docs/VALIDATION.md`。

## 风险与注意事项

官方资产位于 `A题/`，必须保持只读。Q1 推荐候选 M1 仍为 PENDING_CONFIRMATION；B0 必须保留为 Baseline。Q4 动态半径问题仍只阻塞 Q4 MODEL IMPLEMENTATION。仓库为 Public，CI 未作为 Gate 依赖；Git 的 `main` 已与 `origin/main` 同步。
