# Current Project State

> 本文件只描述当前真实状态，不记录历史过程。每次重要工作阶段结束时更新，并保持简短。

## 比赛与赛题

- 比赛：2026 高教社杯全国大学生数学建模竞赛
- 赛题：A题《药材的烘干问题》
- 官方源：`A题/`（OFFICIAL_SOURCE / IMMUTABLE_SOURCE）
- 当前阶段：Q1 SURFACE ERROR AUDIT COMPLETE；Q2/Q3/Q4 按用户要求暂停

## 各问题状态

| 问题 | 状态 | 当前结论 | 证据 |
|---|---|---|---|
| Q1 | FROZEN / COMPLETE；AUDIT COMPLETE | 温度初始 Robin 表示相容；水分初始层诊断成立；边界聚类保守 FVM + 首步 BE/随后 BDF2 完成冻结生产门；本轮独立 uniform-grid BE 审计确认 r=1.9 cm 早期 signed error 穿零，归类 cancellation dip；final workbook、图表包和官方源均未改动 | `experiments/EXP-Q1-SURFACE-DECAY/`、`experiments/EXP-003/`、`experiments/EXP-004/`、`deliverables/final/result1.xlsx` |
| Q2 | DESIGN COMPLETE / IMPLEMENTATION NOT STARTED / HALTED | 已完成设计与契约草案；按用户要求本轮不继续 Q2，不实现 solver，不生成结果 | `docs/Q2_PLAN.md`、`experiments/EXP-Q2-PROPERTY-POINTS/`、`experiments/EXP-Q2-ENV-TAIL/` |
| Q3 | NOT STARTED | 尚未建立模型 | — |
| Q4 | NOT STARTED | 尚未建立模型 | — |

## 当前方案

- 已完成：官方题目与资产登记、Q1-Q4 注册、输入与模板校验基础设施、Q1 Model Design/实现/验证/全时域收敛/冻结交付/可视化；Q2 Model Design & Contract Gate；Q2 只读物性与环境尾段审计
- 当前主模型/主方案：Q1 M1 物理模型保持冻结；Q2 设计主候选为 Q2-M1 固定半径一维径向变物性温度–水分耦合，数值候选 A/B 尚未选择或实现
- Baseline：B0；M2 常-D径向模型和 M3 Dirichlet 模型已完成对照
- 当前最好结果：全时域生产候选温度最大估计不确定度 `1.4012e-6 °C`，含水率最大估计不确定度 `2.7414e-5 kg/kg`；空间细层最大值分别 `3.5588e-7 °C` / `1.2258e-6 kg/kg`，时间细层最大值分别 `4.2626e-7 °C` / `5.5889e-6 kg/kg`
- 正在进行的实验：NONE；Q1 表面 signed-error/边界/分离收敛审计已完成，Q2/Q3/Q4 暂停；`Q1_FREEZE_RUN` 两次内部全场 SHA-256 一致，candidate/final 字节 SHA-256 一致，最终工作簿 70 个论文追踪点、图表 20 个随机数据点均通过

## 风险与下一步

- 主要问题：Q1 的 20–40 s 近表面绝对误差深谷已证明是 signed zero-crossing/cancellation dip，不得写成算法突然提速；Q2 尾段环境、插值、`h/hm`、变系数界面平均、终点和精度门仍是设计开放项
- Blockers：等待用户决定是否结束/继续 Q1 论文整理；Q2/Q3/Q4 暂停，Q2 尚无正式数值结果
- 实现边界兼容标记：`Q2 | NOT STARTED` 仅指 Q2 solver/result2 实现，Q2 设计 Gate 已完成
- 最高优先级任务：审阅 Q1 signed-error 审计证据，保持 Q1 产物、冻结行为与 `A题/` 官方源只读；不要把 cancellation dip 写成收敛优越性
- 推荐下一步：仅在用户明确要求后再恢复 Q2；在此之前不要生成 `result2.xlsx`，不要启动 Q3/Q4

## 更新时间

- 最后更新时间：2026-09-11（Q1 signed-error/边界/时间空间分离收敛审计完成；Q2/Q3/Q4 暂停）
