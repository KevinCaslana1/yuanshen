# Q1 Result & Deliverable Audit

状态：`COMPLETE_PENDING_HUMAN_Q1_FREEZE_APPROVAL`

日期：2026-09-11

冻结运行代码提交：`a40ca42`

本文件是 Q1 最终数值精度与交付门的人工审查包，不是论文正文。candidate 已生成但不是 final；最终复制仍需人工确认。

## Gate Decision

`Q1 RESULT & DELIVERABLE GATE = COMPLETE`

按 `D-Q1-NUM-ACCURACY-CRITERION`，完整交付网格和论文展示点的估计离散不确定度均已通过；四位小数差异仅作辅助诊断。`Q1_FREEZE_RUN` 已双跑通过，`deliverables/candidate/result1.xlsx` 已从 `run_1` 冻结源生成并通过验证；`deliverables/final/` 仍为空。

## Resolved Q1 Decisions

- `D-Q1-OQ005`：A列时间为 `1,2,...,1800 s`，不写 `t=0` 行；这是团队交付决定，不是官方事实。
- `D-Q1-OQ006`：`hm` 直接作用于干基浓度 `C`，不乘空气密度、材料密度或其他未给因子；这是当前建模假设，不是官方唯一解释。
- `D-Q1-OQ007`：中心和表面采用内部 solver 节点值，输出网格严格对齐 `0.0,0.1,...,2.0 cm`，不做输出插值。
- `D-Q1-OQ008`：在题面给定参数体系下，本模型不额外引入需要新增未知参数的耦合项；不得表述为真实过程不存在潜热或交叉耦合。

## Accuracy Scope

- 完整交付网格：`1800` 个时间行 × `21` 个空间列，即每个字段 `37800` 个单元格。
- 论文追踪点：`7` 个时刻 `100,300,600,900,1200,1500,1800 s` × `5` 个距离 `0,0.5,1,1.5,2 cm`，即每个字段 `35` 个单元格。
- Level A：记录原始值的最大绝对差和平均绝对差。
- Level B：使用 `ROUND_HALF_UP` 记录四位小数状态；本轮为辅助认证，不替代主要离散不确定度门。

## Full-Horizon Production Evidence

- 空间：`EXP-Q1-FULL-SPATIAL` 的 base320/base640/base1280 三层空间比较，细层最大估计不确定度为温度 `3.5588e-7 °C`、含水率 `1.2258e-6 kg/kg`。
- 时间：`EXP-Q1-FULL-TEMPORAL` 的 BDF2 `dt=0.25/0.125/0.0625 s` 三层比较，细层最大估计不确定度为温度 `4.2626e-7 °C`、含水率 `5.5889e-6 kg/kg`。
- 最低成本通过配置：边界聚簇保守 FVM，base320 请求网格（实际338区间），`dt=0.25 s`；选定配置合成最大估计不确定度为温度 `1.4012e-6 °C`、含水率 `2.7414e-5 kg/kg`，均 `<5e-5`。
- 初始层表面检查：t=`1,10,60,100,300,600,1800 s` 的温度/含水率不确定度均低于门，未见晚期增加。

## Historical Pre-Freeze Configurations

固定模型为 M1：一维径向 FVM、隐式 Backward Euler、Robin 换热/传质边界、线性边界输入插值、单场 Picard 水分求解。空间细化固定 `dt=0.25 s`，时间细化固定 `N=320`。

| Comparison | Full-grid raw max | Full-grid Level B | Paper-point Level B | Result |
|---|---:|---|---|---|
| N80 → N160 | T `9.1976e-5 K`; C `0.01206546 kg/kg` | T `5472/37800`; C `10235/37800` | T `6/35`; C `8/35` | BLOCKED |
| N160 → N320 | T `2.2996e-5 K`; C `0.00565132 kg/kg` | T `1398/37800`; C `4468/37800` | T `1/35`; C `4/35` | BLOCKED |
| dt1 → dt0.25 | T `0.00143237 K`; C `0.00315888 kg/kg` | T `36498/37800`; C `6926/37800` | T `33/35`; C `7/35` | BLOCKED |

证据：`experiments/EXP-Q1-FINAL-CONV/metrics.json`。完整 Level A、Level B 报告、差异位置和运行配置均保存在该实验目录。

## Current Frozen Selection Status

按团队数值标准选择最低成本通过配置：边界聚簇 base320 请求网格（实际338个区间）、`cluster_power=2`、首步 BE 后固定步长 BDF2 `dt=0.25 s`。该配置由全时域空间/时间证据选出，并在 `Q1_FREEZE_RUN` 从零双跑；两次完整内部输出参考 SHA-256 一致。

## Delivery and Integrity Checks

- Q1 交付契约：已冻结为 `1801 × 22`（含表头行）；candidate 已按该契约生成。
- 官方模板：`A题/附件/附件3/result1.xlsx`，只读；官方源未被写入。
- Candidate：`deliverables/candidate/result1.xlsx` 存在；`scripts/validate_q1_candidate.py` PASS。
- Final：`deliverables/final/result1.xlsx` 不存在。
- 候选校验器：`scripts/validate_q1_candidate.py` 已建立，候选不存在时 fail-closed。
- 论文表追踪：温度 35/35、含水率 35/35 均来自冻结 run_1；随机20个单元格追踪 PASS。论文主张账本仍不自动写入未经人工批准的最终结论。

## Human Audit Decision Required

请人工审查并批准 Q1 冻结配置及 candidate 是否进入 final。批准前不得写入 `deliverables/final/`，不得修改物理模型或数值配置，不得启动 Q2。
