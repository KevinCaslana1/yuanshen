# Handoff

> 本文件保持很短，只服务于新会话、上下文压缩或其他 Agent 的快速接管。

## 当前做到哪里

已完成 PRE-MODELING GATE、Q1 MODEL DESIGN GATE、Q1 IMPLEMENTATION & NUMERICAL VALIDATION GATE、Q1 NUMERICAL CONVERGENCE DIAGNOSIS & REMEDIATION GATE、Q1 INITIAL-LAYER & SURFACE-ACCURACY GATE 和 Q1 FULL-HORIZON PRODUCTION CONFIG FREEZE & CANDIDATE DELIVERABLE GATE。Q1 结果与交付门已完成：候选 `deliverables/candidate/result1.xlsx` 已生成并通过验证，`deliverables/final/` 仍为空，等待人工批准后再进入最终交付。Q2/Q3/Q4 仍为 NOT STARTED。

## 刚刚完成什么

已冻结 Python/依赖和 Q1 交付契约；OQ-005/OQ-006/OQ-007/OQ-008 已登记决策。完成 M1/M2/B0/M3 对照、EXP-001–EXP-007、制造解 benchmark、误差诊断、Picard 敏感性、BDF2 启动对照、表面衰减、聚类 benchmark/短时对照/时间梯、全时段空间与时间收敛验证。完成 `Q1_FREEZE_RUN` 双次从零复跑、确定性检查、内部输出留档、候选工作簿生成、随机 20 单元追溯和纸面表格 35/35 追溯；未生成最终目录工作簿。

## 当前最好结果

生产候选为边界聚类保守径向 FVM + BE 首步/BDF2 + Picard：base320、实际 338 个径向控制体、`dt=.25 s`、0–1800 s 全时段、21 个官方位置。全时段综合估计数值不确定度最大为温度 `1.4012175e-6 °C`、水分 `2.7414225e-5 kg/kg`，均严格小于 `5e-5`。候选已通过格式、有限值、轴线、随机 20 单元和纸面表格追溯验证；舍入歧义仅作为辅助诊断，不构成自动失败。

## 当前主要决策

`A题/` 是 OFFICIAL_SOURCE / IMMUTABLE_SOURCE。正式结果只能从官方模板复制到 `deliverables/candidate/` 后生成。

## 不要重复尝试什么

已记录并修复一次 smoke 入口问题、一次 EXP-003 比较助手问题、一次聚类 BDF2 首步装配分派问题和一次冻结产物时间戳哈希问题；不要把候选工作簿直接放入 `deliverables/final/`，不要修改官方 result 模板，不要把 HYPOTHESIS 写成 FINDING，不要启动 Q2。

## 下一步

请人工审查 `docs/Q1_RESULT_AUDIT.md`、`docs/Q1_INITIAL_LAYER_AUDIT.md` 和 `experiments/Q1_FREEZE_RUN/`，确认冻结生产配置及候选 `result1.xlsx`。获得明确批准后，才可将候选复制到 `deliverables/final/` 并执行最终交付检查；在此之前不得启动 Q2/Q3/Q4。

## 重点阅读文件

`AGENTS.md`、`docs/PROBLEM_SPEC.md`、`docs/DATA_CATALOG.md`、`docs/STATE.md`、`docs/TODO.md`、`docs/RUNBOOK.md`、`docs/VALIDATION.md`。

## 风险与注意事项

官方资产位于 `A题/`，必须保持只读。当前唯一剩余门是人工 Q1 freeze approval：批准前不得写入 `deliverables/final/`。B0 必须保留为 Baseline；Q4 动态半径问题仍只阻塞 Q4 MODEL IMPLEMENTATION。仓库为 Public，CI 未作为 Gate 依赖；当前源代码提交为 `a40ca42`，本轮应只做本地提交，不推送远端。
