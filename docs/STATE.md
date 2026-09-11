# Current Project State

> 本文件只描述当前真实状态，不记录历史过程。每次重要工作阶段结束时更新，并保持简短。

## 比赛与赛题

- 比赛：2026 高教社杯全国大学生数学建模竞赛
- 赛题：A题《药材的烘干问题》
- 官方源：`A题/`（OFFICIAL_SOURCE / IMMUTABLE_SOURCE）
- 当前阶段：Q1 INITIAL-LAYER & SURFACE-ACCURACY GATE

## 各问题状态

| 问题 | 状态 | 当前结论 | 证据 |
|---|---|---|---|
| Q1 | INITIAL-LAYER DIAGNOSIS SUPPORTED / FINAL ACCURACY BLOCKED | 温度初始 Robin 表示相容；均匀初始水分场与表面 Robin 条件不相容，早期表面边界层证据成立；边界聚类保守 FVM 显著降低短时表面空间差异；t=1 s 聚类候选 21 个官方位置中 20 个舍入可认证、表面 1 个仍歧义；未生成 candidate/final 结果 | `docs/Q1_INITIAL_LAYER_AUDIT.md`、`experiments/EXP-Q1-INITIAL-LAYER/`、`experiments/EXP-Q1-SURFACE-DECAY/`、`experiments/EXP-Q1-CLUSTER-TEMPORAL/` |
| Q2 | NOT STARTED | 尚未建立模型 | — |
| Q3 | NOT STARTED | 尚未建立模型 | — |
| Q4 | NOT STARTED | 尚未建立模型 | — |

## 当前方案

- 已完成：官方题目与资产登记、Q1-Q4 注册、输入与模板校验基础设施、Q1 Model Design Gate、Q1 实现与内部数值验证
- 当前主模型/主方案：M1/BE 仍是冻结验证对象；边界聚类保守 FVM 是已 benchmark 并完成短时 Q1 对照的数值候选，尚未冻结；M1-NUM-T2（BE 首步+BDF2）仍是已测试候选，但早期子步未显示优于标准启动
- Baseline：B0；M2 常-D径向模型和 M3 Dirichlet 模型已完成对照
- 当前最好结果：聚类 base1280、`dt=0.0078125 s` 的短时参考给出 `C(R,1s)=2.5177587784 kg/kg`；时间 Richardson 剩余约 `3.1850e-5 kg/kg`，空间剩余约 `1.2259e-6 kg/kg`；独立制造解仍支持空间二阶、BE 时间一阶
- 正在进行的实验：NONE；`EXP-Q1-INITIAL-LAYER`、`EXP-Q1-BDF2-STARTUP`、`EXP-Q1-SURFACE-DECAY`、`EXP-Q1-CLUSTER-BENCH`、`EXP-Q1-CLUSTER-SHORT`、`EXP-Q1-CLUSTER-TEMPORAL` 已完成，最终门仍 BLOCKED

## 风险与下一步

- 主要问题：真实 Q1 表面含水率在 t=1 s 的时间误差仍接近四位小数半单位，聚类候选的表面舍入仍有 1 个歧义位置；聚类策略尚未完成 0–1800 s 全网格复验
- Blockers：完整生产网格 raw/Richardson/舍入门、候选生产配置冻结和人工确认；Q2/Q3/Q4 仍未授权
- 最高优先级任务：审查 `docs/Q1_INITIAL_LAYER_AUDIT.md`，决定是否批准聚类网格及固定启动/切换策略的全时段复验；不得修改初始水分场、放宽门槛或生成工作簿
- 推荐下一步：保持 Q1 BLOCKED；可在人工确认后运行候选全时段验证，当前不生成 candidate/final、不进入最终交付门、不启动 Q2

## 更新时间

- 最后更新时间：2026-09-11（Q1 INITIAL-LAYER & SURFACE-ACCURACY BLOCKED）
