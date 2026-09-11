# Current Project State

> 本文件只描述当前真实状态，不记录历史过程。每次重要工作阶段结束时更新，并保持简短。

## 比赛与赛题

- 比赛：2026 高教社杯全国大学生数学建模竞赛
- 赛题：A题《药材的烘干问题》
- 官方源：`A题/`（OFFICIAL_SOURCE / IMMUTABLE_SOURCE）
- 当前阶段：Q1 FINAL FREEZE, VISUALIZATION & HANDOFF GATE

## 各问题状态

| 问题 | 状态 | 当前结论 | 证据 |
|---|---|---|---|
| Q1 | FROZEN / COMPLETE | 温度初始 Robin 表示相容；水分初始层诊断成立；边界聚类保守 FVM + 首步 BE/随后 BDF2 完成全时域空间/时间门；最低成本生产配置 base320（实际338区间）、dt=0.25 s；candidate 已按人工批准复制到 final，最终工作簿、清单和图表包均通过验证 | `experiments/Q1_FREEZE_RUN/`、`deliverables/candidate/result1.xlsx`、`deliverables/final/result1.xlsx`、`figures/q1/` |
| Q2 | NOT STARTED | 尚未建立模型 | — |
| Q3 | NOT STARTED | 尚未建立模型 | — |
| Q4 | NOT STARTED | 尚未建立模型 | — |

## 当前方案

- 已完成：官方题目与资产登记、Q1-Q4 注册、输入与模板校验基础设施、Q1 Model Design Gate、Q1 实现与内部数值验证、全时域收敛、冻结双跑、candidate/final 交付、最终校验和 Q1 可视化包
- 当前主模型/主方案：Q1 M1 物理模型保持不变；生产数值配置为边界聚簇保守 FVM（cluster_power=2）、首步 BE、随后固定步长 BDF2，base320 请求网格实际338区间，dt=0.25 s
- Baseline：B0；M2 常-D径向模型和 M3 Dirichlet 模型已完成对照
- 当前最好结果：全时域生产候选温度最大估计不确定度 `1.4012e-6 °C`，含水率最大估计不确定度 `2.7414e-5 kg/kg`；空间细层最大值分别 `3.5588e-7 °C` / `1.2258e-6 kg/kg`，时间细层最大值分别 `4.2626e-7 °C` / `5.5889e-6 kg/kg`
- 正在进行的实验：NONE；`Q1_FREEZE_RUN` 两次内部全场 SHA-256 一致，candidate/final 字节 SHA-256 一致，最终工作簿 70 个论文追踪点、图表 20 个随机数据点均通过

## 风险与下一步

- 主要问题：少量 `ROUNDING_AMBIGUOUS` 仅是辅助诊断，不影响已通过的 `<5e-5` 团队数值门；Q1 已完成人工冻结和最终交付
- Blockers：无 Q1 交付阻塞；Q2/Q3/Q4 仍未授权
- 最高优先级任务：保持 Q1 产物与 `A题/` 官方源只读，等待 Q2 model design authorization；不得修改 Q1 冻结模型、初值、Robin 参数或启动策略
- 推荐下一步：不启动 Q2；获得明确授权后再进入 Q2 MODEL DESIGN GATE

## 更新时间

- 最后更新时间：2026-09-11（Q1 FINAL FREEZE, VISUALIZATION & HANDOFF GATE；Q1 frozen）
