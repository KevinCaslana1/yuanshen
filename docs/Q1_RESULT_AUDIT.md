# Q1 Result & Deliverable Audit

状态：`BLOCKED`

日期：2026-09-11

本文件是 Q1 最终数值精度与交付门的人工审查包，不是论文正文，不包含可直接提交的最终结果。

## Gate Decision

`Q1 FINAL NUMERICAL ACCURACY & DELIVERABLE GATE = BLOCKED`

按人工授权的规则，只有在完整交付网格和论文展示点的四位小数输出全部稳定后，才可以生成 `deliverables/candidate/result1.xlsx`。当前条件未满足，因此没有创建 candidate，也没有执行 `Q1_FREEZE_RUN`，更没有写入 `deliverables/final/`。

## Resolved Q1 Decisions

- `D-Q1-OQ005`：A列时间为 `1,2,...,1800 s`，不写 `t=0` 行；这是团队交付决定，不是官方事实。
- `D-Q1-OQ006`：`hm` 直接作用于干基浓度 `C`，不乘空气密度、材料密度或其他未给因子；这是当前建模假设，不是官方唯一解释。
- `D-Q1-OQ007`：中心和表面采用内部 solver 节点值，输出网格严格对齐 `0.0,0.1,...,2.0 cm`，不做输出插值。
- `D-Q1-OQ008`：在题面给定参数体系下，本模型不额外引入需要新增未知参数的耦合项；不得表述为真实过程不存在潜热或交叉耦合。

## Accuracy Scope

- 完整交付网格：`1800` 个时间行 × `21` 个空间列，即每个字段 `37800` 个单元格。
- 论文追踪点：`7` 个时刻 `100,300,600,900,1200,1500,1800 s` × `5` 个距离 `0,0.5,1,1.5,2 cm`，即每个字段 `35` 个单元格。
- Level A：记录原始值的最大绝对差和平均绝对差。
- Level B：使用 `ROUND_HALF_UP` 比较四位小数后的每一个单元格；本门要求所有单元格稳定。

## Tested Configurations

固定模型为 M1：一维径向 FVM、隐式 Backward Euler、Robin 换热/传质边界、线性边界输入插值、单场 Picard 水分求解。空间细化固定 `dt=0.25 s`，时间细化固定 `N=320`。

| Comparison | Full-grid raw max | Full-grid Level B | Paper-point Level B | Result |
|---|---:|---|---|---|
| N80 → N160 | T `9.1976e-5 K`; C `0.01206546 kg/kg` | T `5472/37800`; C `10235/37800` | T `6/35`; C `8/35` | BLOCKED |
| N160 → N320 | T `2.2996e-5 K`; C `0.00565132 kg/kg` | T `1398/37800`; C `4468/37800` | T `1/35`; C `4/35` | BLOCKED |
| dt1 → dt0.25 | T `0.00143237 K`; C `0.00315888 kg/kg` | T `36498/37800`; C `6926/37800` | T `33/35`; C `7/35` | BLOCKED |

证据：`experiments/EXP-Q1-FINAL-CONV/metrics.json`。完整 Level A、Level B 报告、差异位置和运行配置均保存在该实验目录。

## Current Selection Status

按“只有通过完整输出级四位小数稳定性才选择最低成本配置”的规则，没有合法的最终选择。程序记录的最细测试配置为 `N=320`、`Δr=0.0000625 m`、`dt=0.25 s`，但其空间和时间比较均为 `false`，不能作为冻结配置或候选结果来源。

## Delivery and Integrity Checks

- Q1 交付契约：已冻结为 `1801 × 22`（含表头行），但验证状态仍为 `Q1_CONTRACT_FROZEN_PENDING_ACCURACY`。
- 官方模板：`A题/附件/附件3/result1.xlsx`，只读；官方源未被写入。
- Candidate：`deliverables/candidate/result1.xlsx` 不存在。
- Final：`deliverables/final/result1.xlsx` 不存在。
- 候选校验器：`scripts/validate_q1_candidate.py` 已建立，候选不存在时 fail-closed。
- 论文账本：未新增任何论文主张或最终表格结论。

## Human Audit Decision Required

请人工决定是否批准下一轮数值整改方案（例如进一步空间/时间细化、检查边界/中心离散实现，或其他可解释且可记录的调整）。在获得明确决定并重新登记实验前，不得生成候选工作簿、放宽四舍五入稳定性门槛或启动 Q2。
