# Problem Specification

> 本文件是赛题要求的唯一事实来源。它只登记正式题面、官方附件和明确的项目解释，不写建模方案、求解算法、仿真结果或论文结论。

## 状态定义

- `STATEMENT_FACT`：可直接由 `A题/A题.pdf` 或官方附件确认的事实。
- `TEAM_INTERPRETATION`：团队为组织 Workflow 做出的解释，不得当作官方条件。
- `OPEN_QUESTION`：题面、模板或当前资产尚未明确，需要人工确认的事项。

## Problem Metadata

| 字段 | 状态 | 内容 |
|---|---|---|
| 比赛名称 | STATEMENT_FACT | 2026 年高教社杯全国大学生数学建模竞赛 |
| 年份 | STATEMENT_FACT | 2026 |
| 题号 | STATEMENT_FACT | A题 |
| 题目名称 | STATEMENT_FACT | 药材的烘干问题 |
| 官方题目文件 | STATEMENT_FACT | `A题/A题.pdf` |
| 官方附件 | STATEMENT_FACT | `A题/附件/附件1.xlsx`、`A题/附件/附件2.xlsx`、`A题/附件/附件3/result1.xlsx` 至 `result4.xlsx` |
| 官方源保护 | TEAM_INTERPRETATION | `A题/` 是 `OFFICIAL_SOURCE / IMMUTABLE_SOURCE`，不直接写入结果 |
| 题面公式与参数 | STATEMENT_FACT | 相关参数见附录2，问题2/3经验公式见附录3，问题4经验公式见附录4 |

## General Units and Precision

| 项目 | 状态 | 规定 |
|---|---|---|
| 温度 | STATEMENT_FACT | 题面输入/输出温度使用 `°C`；附录经验公式中的药材温度 `T` 使用 `K` |
| 水分浓度 | STATEMENT_FACT | `kg/kg` |
| 时间 | STATEMENT_FACT | 按问题分别使用 `s` 或 `h`；完整 Excel 结果的 A 列按附录说明使用 `s` |
| 距离/尺寸 | STATEMENT_FACT | 题面表格和模板使用 `cm` |
| 结果精度 | STATEMENT_FACT | 所有结果保留四位小数 |
| 内部单位记录 | TEAM_INTERPRETATION | 后续程序必须同时记录原始单位、内部计算单位和输出单位，禁止隐式转换 |

## Question Matrix

### Q1

| 字段 | 状态 | 内容 |
|---|---|---|
| 官方要求解决什么 | STATEMENT_FACT | 建立预热平衡阶段药材温度和水分浓度变化规律的数学模型 |
| 初始条件 | STATEMENT_FACT | 药材近似圆柱形，长 `25 cm`、半径 `2 cm`；初始温度 `28°C`；初始水分浓度 `2.55 kg/kg` |
| 输入 | STATEMENT_FACT | 烘房温度和水分浓度随时间的变化见附件1；相关参数见附录2 |
| 论文输出 | STATEMENT_FACT | 按表1给出温度，按表2给出水分浓度；时间为 `100, 300, 600, 900, 1200, 1500, 1800 s`，距离为 `0, 0.5, 1, 1.5, 2 cm` |
| 完整输出 | STATEMENT_FACT | `result1.xlsx`；1800 s 内每隔 `1 s`、到药材中心距离每隔 `0.1 cm` |
| 输出单位 | STATEMENT_FACT | 温度 `°C`；水分浓度 `kg/kg`；时间 `s`；距离 `cm` |
| 对应结果文件 | STATEMENT_FACT | `A题/附件/附件3/result1.xlsx` |
| 对应 Excel Sheet | STATEMENT_FACT | `温度`、`水分浓度` |
| 相关附件 | STATEMENT_FACT | 附件1、附录2、附件3/result1.xlsx |
| 题面限制 | OPEN_QUESTION | 具体离散边界处理、数值方法和内部单位转换尚未登记；本文件不作推断 |

### Q2

| 字段 | 状态 | 内容 |
|---|---|---|
| 官方要求解决什么 | STATEMENT_FACT | 建立整个烘干过程药材温度和水分浓度变化规律的数学模型 |
| 输入/依据 | STATEMENT_FACT | 预热平衡与恒温干燥阶段参数不同；问题2使用附录3中的经验公式 |
| 论文输出 | STATEMENT_FACT | 按表3、表4给出 `3 h` 内每隔 `0.5 h`、距离 `0, 0.5, 1, 1.5, 2 cm` 的温度和水分浓度 |
| 完整输出 | STATEMENT_FACT | `result2.xlsx`；每隔 `1 s`、距离每隔 `0.1 cm` |
| 输出单位 | STATEMENT_FACT | 温度 `°C`；水分浓度 `kg/kg`；论文表时间 `h`；完整 Excel 时间列 `s`；距离 `cm` |
| 对应结果文件 | STATEMENT_FACT | `A题/附件/附件3/result2.xlsx` |
| 对应 Excel Sheet | STATEMENT_FACT | `温度`、`水分浓度` |
| 相关附件 | STATEMENT_FACT | 附件1、附录3、附件3/result2.xlsx |
| 题面限制 | OPEN_QUESTION | 题面提到烘干过程一般持续2-3天，但本问明确的论文展示区间为3小时；更长时段的实现边界待后续人工确认 |

### Q3

| 字段 | 状态 | 内容 |
|---|---|---|
| 官方要求解决什么 | STATEMENT_FACT | 按烘干要求确定药材各处水分浓度低于 `0.15 kg/kg` 所需的烘干时间 |
| 阈值 | STATEMENT_FACT | 药材各处水分浓度应低于 `0.15 kg/kg` |
| 论文输出 | STATEMENT_FACT | 按表5给出每隔 `6 h`、距离每隔 `0.5 cm` 的水分浓度，并包含烘干结束时间行 |
| 完整输出 | STATEMENT_FACT | `result3.xlsx`；内部水分浓度每隔 `60 s`、距离每隔 `0.1 cm` |
| 输出单位 | STATEMENT_FACT | 烘干时间 `h`；完整 Excel 时间列 `s`；距离 `cm`；水分浓度 `kg/kg` |
| 对应结果文件 | STATEMENT_FACT | `A题/附件/附件3/result3.xlsx` |
| 对应 Excel Sheet | STATEMENT_FACT | `Sheet1` |
| 相关附件 | STATEMENT_FACT | 附录3、附件3/result3.xlsx |
| 题面限制 | OPEN_QUESTION | “烘干结束时间”在输出表中的具体行填充方式及边界判断的实现细节待人工确认 |

### Q4

| 字段 | 状态 | 内容 |
|---|---|---|
| 官方要求解决什么 | STATEMENT_FACT | 根据附件2确定考虑水分流失导致尺寸变化时的药材烘干时长 |
| 输入/依据 | STATEMENT_FACT | 附件2给出各时间点药材半径；相关经验公式见附录4 |
| 论文输出 | STATEMENT_FACT | 按表6给出每隔 `6 h`、距离每隔 `0.5 cm` 的水分浓度，距离终点为药材表面，并包含烘干结束时间行 |
| 完整输出 | STATEMENT_FACT | `result4.xlsx`；内部水分浓度每隔 `60 s`、距离 `0.1 cm` |
| 输出单位 | STATEMENT_FACT | 烘干时间 `h`；完整 Excel 时间列 `s`；距离 `cm`；水分浓度 `kg/kg`；半径 `cm` |
| 对应结果文件 | STATEMENT_FACT | `A题/附件/附件3/result4.xlsx` |
| 对应 Excel Sheet | STATEMENT_FACT | `Sheet1` |
| 相关附件 | STATEMENT_FACT | 附件2、附录4、附件3/result4.xlsx |
| 题面限制 | OPEN_QUESTION | 变化半径与空间网格的具体同步方式、表6“药材表面”列的最终列数待后续人工确认 |

## Official Excel Structure

以下结构仅为资产登记，不代表已经生成或验证了任何答案：

| 文件 | Sheet | 当前模板骨架 | 结构说明 |
|---|---|---:|---|
| `result1.xlsx` | `温度`、`水分浓度` | 5行 × 6列/Sheet | 第1行含时间/距离标题与 `0, 0.1, 0.2, …, 2` 示例列；A列为时间示例 |
| `result2.xlsx` | `温度`、`水分浓度` | 5行 × 6列/Sheet | 结构与result1模板一致；A列按附录说明为秒 |
| `result3.xlsx` | `Sheet1` | 5行 × 6列 | 第1行含时间/距离标题与 `0, 0.1, 0.2, …, 2` 示例列；A列为秒 |
| `result4.xlsx` | `Sheet1` | 5行 × 6列 | 第1行末列标为“药材表面”；A列为秒 |

## Open Questions Register

| ID | 未决事项 | 来源 | 进入建模前的处理 |
|---|---|---|---|
| OQ-001 | DELIVERABLE | 题面输出表与完整 Excel 的时间单位不同，需在实现和论文中分别保留 | DELIVERABLE GENERATION | 团队与人工审查；显式记录，不做隐式转换 |
| OQ-002 | INTERPRETATION | Q2“3小时展示”与“烘干一般2-3天”的关系 | MODEL IMPLEMENTATION | 人工确认官方要求、背景描述和团队解释的边界 |
| OQ-003 | DELIVERABLE | Q3/Q4 烘干结束时间行的写入格式 | DELIVERABLE GENERATION | 人工确认后登记到 Deliverable Contract |
| OQ-004 | MODELING | Q4 半径变化与空间网格的同步方式 | MODEL IMPLEMENTATION | 建模负责人在进入 Q4 实现时处理；不阻塞当前 PRE-MODELING WORKFLOW |
| OQ-005 | DELIVERABLE | Q1 `result1.xlsx` 完整结果是否包含 `t=0` 行；模板示例从1开始但不应替代题面要求 | DELIVERABLE GENERATION | Q1 实现前人工确认；不在设计阶段硬编码最终行数 |
| OQ-006 | MODELING | Q1 对流传质系数 `hm` 与干基水分浓度 `C` 的 Robin 边界物理解释及符号约定 | MODEL IMPLEMENTATION | Q1 实现前人工审查，并用 smoke test 检查边界通量方向 |
| OQ-007 | NUMERICAL | Q1 `r=0` 与 `r=R` 的完整输出值采用节点值、边界值还是插值值 | NUMERICAL IMPLEMENTATION | 在网格定义与交付契约中登记，保持端点规则可追溯 |
| OQ-008 | MODELING | Q1 是否需要潜热、热质交叉耦合或内部源项 | MODEL IMPLEMENTATION | 题面未给出相关参数，当前不自行扩展；需人工确认高影响假设 |
