# Handoff

> 本文件保持很短，只服务于新会话、上下文压缩或其他 Agent 的快速接管。

## 当前做到哪里

已完成 PRE-MODELING GATE、Q1 MODEL DESIGN GATE 和 Q1 IMPLEMENTATION & NUMERICAL VALIDATION GATE；Q1 内部实现与 EXP-001–EXP-007 已完成，等待人工授权进入 Result & Deliverable Gate。Q2/Q3/Q4 仍为 NOT STARTED。

## 刚刚完成什么

已冻结 Python/依赖、Deliverable Contract、Contract Validator、Workflow 测试和官方路径保护。Q1 已完成官方 PDF/附件1/result1 复核、变量单位表、候选模型、Baseline、假设、数值策略、实现、M1/M2/B0/M3 对照和 EXP-001–EXP-007 验证证据。

## 当前最好结果

M1 内部验证通过；EXP-002 的 M1 体积加权平均结果为 `35.1690 °C`、`2.293482 kg/kg`。这些不是论文最终结论，且尚未生成 `result1.xlsx`。

## 当前主要决策

`A题/` 是 OFFICIAL_SOURCE / IMMUTABLE_SOURCE。正式结果只能从官方模板复制到 `deliverables/candidate/` 后生成。

## 不要重复尝试什么

已记录并修复一次 smoke 入口问题和一次 EXP-003 比较助手问题；不要把内部实验直接写成论文结论，不要生成 `result1.xlsx`，不要修改官方 result 模板，不要把 HYPOTHESIS 写成 FINDING。

## 下一步

等待人工确认 OQ-005/OQ-006/OQ-007/OQ-008 以及是否允许生成 candidate `result1.xlsx`，然后进入 Q1 RESULT & DELIVERABLE GATE。Q2/Q3/Q4 不得自动启动。

## 重点阅读文件

`AGENTS.md`、`docs/PROBLEM_SPEC.md`、`docs/DATA_CATALOG.md`、`docs/STATE.md`、`docs/TODO.md`、`docs/RUNBOOK.md`、`docs/VALIDATION.md`。

## 风险与注意事项

官方资产位于 `A题/`，必须保持只读。Q1 推荐候选 M1 仍为 PENDING_CONFIRMATION；B0 必须保留为 Baseline。Q4 动态半径问题仍只阻塞 Q4 MODEL IMPLEMENTATION。仓库为 Public，CI 未作为 Gate 依赖；正式模型代码和实验结果不得推送到远端。
