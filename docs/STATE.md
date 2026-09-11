# Current Project State

> 本文件只描述当前真实状态，不记录历史过程。每次重要工作阶段结束时更新，并保持简短。

## 比赛与赛题

- 比赛：2026 高教社杯全国大学生数学建模竞赛
- 赛题：A题《药材的烘干问题》
- 官方源：`A题/`（OFFICIAL_SOURCE / IMMUTABLE_SOURCE）
- 当前阶段：Q1 NUMERICAL CONVERGENCE DIAGNOSIS & REMEDIATION GATE

## 各问题状态

| 问题 | 状态 | 当前结论 | 证据 |
|---|---|---|---|
| Q1 | NUMERICAL REMEDIATION BLOCKED | M1/BE 生产实现审计通过；独立制造解支持空间二阶、BE 时间一阶；误差定位显示含水率早期/表面误差主导；BDF2 候选改善论文点但完整网格安全裕量仍不足；未生成 candidate/final 结果 | `docs/Q1_NUMERICAL_REMEDIATION_AUDIT.md`、`experiments/EXP-Q1-NUM-DIAG/`、`experiments/EXP-Q1-NUM-REMEDIATION/` |
| Q2 | NOT STARTED | 尚未建立模型 | — |
| Q3 | NOT STARTED | 尚未建立模型 | — |
| Q4 | NOT STARTED | 尚未建立模型 | — |

## 当前方案

- 已完成：官方题目与资产登记、Q1-Q4 注册、输入与模板校验基础设施、Q1 Model Design Gate、Q1 实现与内部数值验证
- 当前主模型/主方案：M1/BE 仍是冻结验证对象；M1-NUM-T2（BE 首步+BDF2）是已测试候选，但尚未通过最终数值精度门，不能称为最终冻结模型
- Baseline：B0；M2 常-D径向模型和 M3 Dirichlet 模型已完成对照
- 当前最好结果：独立制造解 benchmark 的 BE 空间 L∞ 阶约 `1.97–2.00`、时间 L∞ 阶约 `0.99–1.01`；BDF2 在论文 7×5 点 `dt=0.5→0.25 s` 达到温度/含水率 `0/35` 四舍五入差异，但不是全网格通过证据
- 正在进行的实验：NONE；`EXP-Q1-NUM-BENCH`、`EXP-Q1-NUM-DIAG`、`EXP-Q1-PICARD-SENS`、`EXP-Q1-NUM-REMEDIATION` 已完成，最终门仍 BLOCKED

## 风险与下一步

- 主要问题：BE 的真实 Q1 时间误差和含水率早期/表面误差在完整网格上仍超过四位小数安全裕量；BDF2 候选尚未消除该问题
- Blockers：`EXP-Q1-FINAL-CONV` 与 `EXP-Q1-NUM-REMEDIATION` 的完整网格安全门；需要人工决定是否进行针对早期/表面误差的最小附加诊断；Q2/Q3/Q4 仍未授权
- 最高优先级任务：人工审查 `docs/Q1_NUMERICAL_REMEDIATION_AUDIT.md`，决定是否批准下一轮局部数值诊断；不得直接追求无限细化或放宽门槛
- 推荐下一步：保持 Q1 BLOCKED；在人工确认前不生成候选文件、不运行完整结果冻结、不启动 Q2

## 更新时间

- 最后更新时间：2026-09-11（Q1 NUMERICAL REMEDIATION BLOCKED）
