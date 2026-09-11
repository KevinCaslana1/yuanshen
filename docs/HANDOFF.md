# Handoff

> 本文件保持很短，只服务于新会话、上下文压缩或其他 Agent 的快速接管。

## 当前做到哪里

已完成 PRE-MODELING GATE、Q1 MODEL DESIGN GATE 和 Q1 IMPLEMENTATION & NUMERICAL VALIDATION GATE；Q1 FINAL NUMERICAL ACCURACY 先被 EXP-Q1-FINAL-CONV 阻塞，随后已进入并完成 Q1 NUMERICAL CONVERGENCE DIAGNOSIS & REMEDIATION GATE。生产实现审计和独立 benchmark 通过，但 BDF2 候选的完整网格安全裕量仍不足，当前整改门仍阻塞。Q2/Q3/Q4 仍为 NOT STARTED。

## 刚刚完成什么

已冻结 Python/依赖和 Q1 交付契约；OQ-005/OQ-006/OQ-007/OQ-008 已登记决策。完成 M1/M2/B0/M3 对照、EXP-001–EXP-007、EXP-Q1-FINAL-CONV，以及本轮 `EXP-Q1-NUM-BENCH`、`EXP-Q1-NUM-DIAG`、`EXP-Q1-PICARD-SENS`、`EXP-Q1-NUM-REMEDIATION`。新增 Robin/中心/BDF2 边界测试和 M1-NUM-T2 候选；未生成任何结果工作簿。

## 当前最好结果

独立 benchmark 支持 BE 空间二阶、时间一阶；真实 Q1 的 BDF2 候选在论文 7×5 点 `dt=0.5→0.25 s` 达到温度/含水率 `0/35` 四舍五入差异，但全网格含水率 Richardson 剩余估计仍为 `0.0006163 kg/kg`。这些不是论文最终结论，且尚未生成 `result1.xlsx`。

## 当前主要决策

`A题/` 是 OFFICIAL_SOURCE / IMMUTABLE_SOURCE。正式结果只能从官方模板复制到 `deliverables/candidate/` 后生成。

## 不要重复尝试什么

已记录并修复一次 smoke 入口问题和一次 EXP-003 比较助手问题；不要把内部实验直接写成论文结论，不要生成 `result1.xlsx`，不要修改官方 result 模板，不要把 HYPOTHESIS 写成 FINDING。

## 下一步

等待人工审查 `docs/Q1_NUMERICAL_REMEDIATION_AUDIT.md`，决定是否进行针对早期/表面含水率误差的最小附加诊断；在人工确认前不得生成 candidate `result1.xlsx`、进入 freeze run 或启动 Q2/Q3/Q4。

## 重点阅读文件

`AGENTS.md`、`docs/PROBLEM_SPEC.md`、`docs/DATA_CATALOG.md`、`docs/STATE.md`、`docs/TODO.md`、`docs/RUNBOOK.md`、`docs/VALIDATION.md`。

## 风险与注意事项

官方资产位于 `A题/`，必须保持只读。M1/BE 是当前冻结验证对象但未通过精度门，M1-NUM-T2 只是候选；B0 必须保留为 Baseline。Q4 动态半径问题仍只阻塞 Q4 MODEL IMPLEMENTATION。仓库为 Public，CI 未作为 Gate 依赖；本轮已做本地提交但按授权不推送远端。
