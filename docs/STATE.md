# Current Project State

> 本文件只描述当前真实状态，不记录历史过程。每次重要工作阶段结束时更新，并保持简短。

## 比赛与赛题

- 比赛：2026 高教社杯全国大学生数学建模竞赛
- 赛题：A题《药材的烘干问题》
- 官方源：`A题/`（OFFICIAL_SOURCE / IMMUTABLE_SOURCE）
- 当前阶段：Q1 IMPLEMENTATION & NUMERICAL VALIDATION

## 各问题状态

| 问题 | 状态 | 当前结论 | 证据 |
|---|---|---|---|
| Q1 | IMPLEMENTATION & NUMERICAL VALIDATION COMPLETE / WAITING RESULT GATE APPROVAL | M1、M2、B0、M3 已实现；EXP-001–EXP-007 已按序完成并通过运行检查；未生成最终交付结果 | `docs/Q1_PLAN.md`、`docs/EXPERIMENTS.md` |
| Q2 | NOT STARTED | 尚未建立模型 | — |
| Q3 | NOT STARTED | 尚未建立模型 | — |
| Q4 | NOT STARTED | 尚未建立模型 | — |

## 当前方案

- 已完成：官方题目与资产登记、Q1-Q4 注册、输入与模板校验基础设施、Q1 Model Design Gate、Q1 实现与内部数值验证
- 当前主模型/主方案：M1 为已验证的实现候选，但尚未冻结为最终模型
- Baseline：B0；M2 常-D径向模型和 M3 Dirichlet 模型已完成对照
- 当前最好结果：M1 在 EXP-001–EXP-007 的运行与守恒/范围检查中通过；EXP-002 平均温度 `35.1690 °C`、平均水分 `2.29348 kg/kg`（内部证据，非论文最终结论）
- 正在进行的实验：NONE；EXP-001–EXP-007 均为 COMPLETED

## 风险与下一步

- 主要问题：Q1 内部验证已完成，但最终主模型、`hm` 解释、端点交付规则和是否加入额外物理仍需人工确认
- Blockers：Q1 RESULT & DELIVERABLE GATE 的人工授权；Q2/Q3/Q4 仍未授权
- 最高优先级任务：人工审查 OQ-005/OQ-006/OQ-007/OQ-008，并决定是否允许生成 candidate `result1.xlsx`
- 推荐下一步：等待 Q1 RESULT & DELIVERABLE GATE 授权；不得启动 Q2，不得自动生成最终 `result1.xlsx`

## 更新时间

- 最后更新时间：2026-09-11（Q1 IMPLEMENTATION & NUMERICAL VALIDATION COMPLETE / WAITING RESULT GATE APPROVAL）
