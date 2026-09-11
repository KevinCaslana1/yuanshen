# Current Project State

> 本文件只描述当前真实状态，不记录历史过程。每次重要工作阶段结束时更新，并保持简短。

## 比赛与赛题

- 比赛：2026 高教社杯全国大学生数学建模竞赛
- 赛题：A题《药材的烘干问题》
- 官方源：`A题/`（OFFICIAL_SOURCE / IMMUTABLE_SOURCE）
- 当前阶段：Q1 FINAL NUMERICAL ACCURACY & DELIVERABLE GATE

## 各问题状态

| 问题 | 状态 | 当前结论 | 证据 |
|---|---|---|---|
| Q1 | NUMERICAL ACCURACY BLOCKED | M1、M2、B0、M3 已实现；EXP-001–EXP-007 通过内部检查，但 EXP-Q1-FINAL-CONV 未通过完整网格四位小数稳定性；未生成 candidate/final 结果 | `docs/Q1_PLAN.md`、`docs/EXPERIMENTS.md`、`experiments/EXP-Q1-FINAL-CONV/` |
| Q2 | NOT STARTED | 尚未建立模型 | — |
| Q3 | NOT STARTED | 尚未建立模型 | — |
| Q4 | NOT STARTED | 尚未建立模型 | — |

## 当前方案

- 已完成：官方题目与资产登记、Q1-Q4 注册、输入与模板校验基础设施、Q1 Model Design Gate、Q1 实现与内部数值验证
- 当前主模型/主方案：M1 是冻结验证对象，但尚未通过最终数值精度门，不能称为最终冻结模型
- Baseline：B0；M2 常-D径向模型和 M3 Dirichlet 模型已完成对照
- 当前最好结果：M1 在 EXP-001–EXP-007 的运行与守恒/范围检查中通过；EXP-Q1-FINAL-CONV 的最细测试仍被四位小数输出稳定性阻塞（内部证据，非论文最终结论）
- 正在进行的实验：NONE；EXP-001–EXP-007 为 COMPLETED，EXP-Q1-FINAL-CONV 为 BLOCKED

## 风险与下一步

- 主要问题：当前 M1/离散配置在完整交付网格上未达到四位小数稳定性，无法生成 candidate `result1.xlsx`
- Blockers：EXP-Q1-FINAL-CONV 输出级精度门；需要人工决定数值整改方案；Q2/Q3/Q4 仍未授权
- 最高优先级任务：审查 N160→N320 与 dt1→dt0.25 的输出差异，并批准下一轮数值整改范围
- 推荐下一步：保持 Q1 BLOCKED，等待人工数值审查；不得放宽门槛、生成候选文件或启动 Q2

## 更新时间

- 最后更新时间：2026-09-11（Q1 NUMERICAL ACCURACY BLOCKED）
