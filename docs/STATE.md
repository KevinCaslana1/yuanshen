# Current Project State

> 本文件只描述当前真实状态，不记录历史过程。每次重要工作阶段结束时更新，并保持简短。

## 比赛与赛题

- 比赛：2026 高教社杯全国大学生数学建模竞赛
- 赛题：A题《药材的烘干问题》
- 官方源：`A题/`（OFFICIAL_SOURCE / IMMUTABLE_SOURCE）
- 当前阶段：Q1 FROZEN；Q2 IMPLEMENTATION & SHORT-HORIZON VALIDATION COMPLETE；等待 Q2 长时/交付授权；Q3/Q4 未启动

## 各问题状态

| 问题 | 状态 | 当前结论 | 证据 |
|---|---|---|---|
| Q1 | FROZEN / COMPLETE；AUDIT COMPLETE | 温度初始 Robin 表示相容；水分初始层诊断成立；边界聚类保守 FVM + 首步 BE/随后 BDF2 完成冻结生产门；本轮独立 uniform-grid BE 审计确认 r=1.9 cm 早期 signed error 穿零，归类 cancellation dip；final workbook、图表包和官方源均未改动 | `experiments/EXP-Q1-SURFACE-DECAY/`、`experiments/EXP-003/`、`experiments/EXP-004/`、`deliverables/final/result1.xlsx` |
| Q2 | IMPLEMENTATION & SHORT-HORIZON VALIDATION COMPLETE / WAITING LONG-HORIZON AUTHORIZATION | Q2-M1 独立实现、性质/环境层、变量系数 FVM、coupled Picard、checkpoint/restart、0–1800 s 敏感性与0–10800 s内部验证完成；未生成 `result2.xlsx`；环境尾段、PCHIP、界面平均、h/hm、终点和精度门仍 OPEN | `src/q2/`、`experiments/EXP-Q2-001/`–`EXP-Q2-011/`、`docs/EXPERIMENTS.md` |
| Q3 | NOT STARTED | 尚未建立模型 | — |
| Q4 | NOT STARTED | 尚未建立模型 | — |

## 当前方案

- 已完成：官方题目与资产登记、Q1-Q4 注册、输入与模板校验基础设施、Q1 Model Design/实现/验证/全时域收敛/冻结交付/可视化；Q2 Model Design、实现、独立 benchmark、耦合/敏感性/重启/0–3 h 短时验证
- 当前主模型/主方案：Q1 M1 生产行为保持冻结；Q2-M1 固定半径一维径向变物性温度–水分耦合已实现；Candidate A 的 clustered FVM + BE startup/BDF2 记录为 `RECOMMENDED_FOR_Q2_FREEZE`，不是 FINAL
- Baseline：B0；M2 常-D径向模型和 M3 Dirichlet 模型已完成对照
- 当前最好结果：全时域生产候选温度最大估计不确定度 `1.4012e-6 °C`，含水率最大估计不确定度 `2.7414e-5 kg/kg`；空间细层最大值分别 `3.5588e-7 °C` / `1.2258e-6 kg/kg`，时间细层最大值分别 `4.2626e-7 °C` / `5.5889e-6 kg/kg`
- 正在进行的实验：NONE；Q2 实验已完成并保留证据，Q3/Q4 未启动；Q1 `result1.xlsx` SHA-256 仍为 `06b67b1f688d84a701ac4d2f4b0f47a1624069877df6724faf071a48af177b5c`，Q1 freeze reference SHA-256 仍为 `f13667b5fe8e4c1e1a7635b18ab4c7aaa9e3fef5111b893a9ce79b6deb3fad17`

## 风险与下一步

- 主要问题：Q1 的20–40 s近表面绝对误差深谷已证明是 signed zero-crossing/cancellation dip，不得写成算法突然提速；Q2 的 `OQ-Q2-ENV-001/002`、`OQ-Q2-BC-001`、`OQ-Q2-FVM-001`、`OQ-Q2-END-001`、`OQ-Q2-ACC-001` 仍未决
- Blockers：Q2 不能进入正式 `result2.xlsx`/长时全程交付，除非人工确认开放问题和交付终点；Q3/Q4 未授权
- 实现边界兼容标记：Q2 本轮只完成 implementation & short-horizon validation；不包含 Q2 final deliverable、不包含 Q3/Q4
- 最高优先级任务：保持 Q1 冻结资产和 `A题/` 只读；审阅 Q2 开放问题与 EXP-Q2 证据；不得把 Q2 的数值 proxy 写成物理优越性或最终论文结论
- 推荐下一步：人工决定 Q2 环境尾段/插值/边界/界面平均/终点/精度门后，再单独授权正式交付；在此前不要生成 `result2.xlsx`，不要启动 Q3/Q4

## 更新时间

- 最后更新时间：2026-09-11（Q2 implementation & short-horizon validation 完成；未生成 result2，Q3/Q4 未启动）
