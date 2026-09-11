# Current Project State

> 本文件只描述当前真实状态，不记录历史过程。每次重要工作阶段结束时更新，并保持简短。

## 比赛与赛题

- 比赛：2026 高教社杯全国大学生数学建模竞赛
- 赛题：A题《药材的烘干问题》
- 官方源：`A题/`（OFFICIAL_SOURCE / IMMUTABLE_SOURCE）
- 当前阶段：Q2 MODEL DESIGN & CONTRACT GATE

## 各问题状态

| 问题 | 状态 | 当前结论 | 证据 |
|---|---|---|---|
| Q1 | FROZEN / COMPLETE | 温度初始 Robin 表示相容；水分初始层诊断成立；边界聚类保守 FVM + 首步 BE/随后 BDF2 完成全时域空间/时间门；最低成本生产配置 base320（实际338区间）、dt=0.25 s；candidate 已按人工批准复制到 final，最终工作簿、清单和图表包均通过验证 | `experiments/Q1_FREEZE_RUN/`、`deliverables/candidate/result1.xlsx`、`deliverables/final/result1.xlsx`、`figures/q1/` |
| Q2 | MODEL DESIGN COMPLETE / IMPLEMENTATION NOT STARTED | 已完成官方要求、附录3物性核对、Q1→Q2差异矩阵、Q2-M1与数值候选、环境/终点开放项、Picard/验证/长时架构和 result2 契约草案；尚未实现 solver 或生成结果 | `docs/Q2_PLAN.md`、`experiments/EXP-Q2-PROPERTY-POINTS/`、`experiments/EXP-Q2-ENV-TAIL/` |
| Q3 | NOT STARTED | 尚未建立模型 | — |
| Q4 | NOT STARTED | 尚未建立模型 | — |

## 当前方案

- 已完成：官方题目与资产登记、Q1-Q4 注册、输入与模板校验基础设施、Q1 Model Design/实现/验证/全时域收敛/冻结交付/可视化；Q2 Model Design & Contract Gate；Q2 只读物性与环境尾段审计
- 当前主模型/主方案：Q1 M1 物理模型保持冻结；Q2 设计主候选为 Q2-M1 固定半径一维径向变物性温度–水分耦合，数值候选 A/B 尚未选择或实现
- Baseline：B0；M2 常-D径向模型和 M3 Dirichlet 模型已完成对照
- 当前最好结果：全时域生产候选温度最大估计不确定度 `1.4012e-6 °C`，含水率最大估计不确定度 `2.7414e-5 kg/kg`；空间细层最大值分别 `3.5588e-7 °C` / `1.2258e-6 kg/kg`，时间细层最大值分别 `4.2626e-7 °C` / `5.5889e-6 kg/kg`
- 正在进行的实验：NONE；Q2 `EXP-Q2-PROPERTY-POINTS` 与 `EXP-Q2-ENV-TAIL` 为已完成的设计阶段只读审计，其余 Q2 实验 PLANNED；`Q1_FREEZE_RUN` 两次内部全场 SHA-256 一致，candidate/final 字节 SHA-256 一致，最终工作簿 70 个论文追踪点、图表 20 个随机数据点均通过

## 风险与下一步

- 主要问题：Q2 尾段环境、插值、`h/hm`、变系数界面平均、终点和精度门仍是显式开放项；Q1 的少量 `ROUNDING_AMBIGUOUS` 仅为辅助诊断，不影响 Q1 冻结
- Blockers：等待人工 Q2 implementation authorization；Q2 尚无正式数值结果；Q3/Q4 未启动
- 实现边界兼容标记：`Q2 | NOT STARTED` 仅指 Q2 solver/result2 实现，Q2 设计 Gate 已完成
- 最高优先级任务：保持 Q1 产物、冻结行为与 `A题/` 官方源只读；确认 Q2 开放决策后再实现 `src/q2/`
- 推荐下一步：人工确认 Q2 决策项并授权小规模实现/pilot；不要生成 `result2.xlsx`，不要启动 Q3/Q4

## 更新时间

- 最后更新时间：2026-09-11（Q2 MODEL DESIGN & CONTRACT GATE COMPLETE；等待 Q2 implementation authorization）
