# Official Data Catalog

> 本目录登记所有官方资产。文件均位于 `A题/`，属于 `OFFICIAL_SOURCE / IMMUTABLE_SOURCE`。哈希和结构用于防止误改；任何哈希变化都需要人工确认。

## Protection Rules

- 官方原始文件不得修改、覆盖、删除、重命名或直接写入。
- `result1.xlsx` 至 `result4.xlsx` 是官方模板，不是结果输出区。
- 生成文件必须从官方模板复制到 `deliverables/candidate/`。
- 本目录不复制官方二进制文件到 `problem/` 或 `data/raw/`。

## Asset Inventory

| Asset ID | 路径 | 类型 | 来源/用途 | 官方原始文件 | 允许修改 | 大小（bytes） | SHA-256 |
|---|---|---|---|---|---|---:|---|
| ASSET-PDF-001 | `A题/A题.pdf` | PDF | 官方题面；登记 Problem Spec | 是 | 否 | 553320 | `052d8014bff5727c019b72e44fdffaf5c145ce04050dd938baaf3527db331736` |
| ASSET-XLSX-001 | `A题/附件/附件1.xlsx` | XLSX | 烘干初期烘房温度和水分浓度 | 是 | 否 | 16586 | `7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7` |
| ASSET-XLSX-002 | `A题/附件/附件2.xlsx` | XLSX | 烘干过程药材半径 | 是 | 否 | 11485 | `5563acbfa4b4afb10cc6c03e2207e5369bf39da27576672aff14cc5c32e704af` |
| ASSET-TPL-001 | `A题/附件/附件3/result1.xlsx` | XLSX模板 | Q1结果模板 | 是 | 否 | 10073 | `23b261b295c1b787d000eebbca6521c37075107b6fcf78724f8d395ce1798ff4` |
| ASSET-TPL-002 | `A题/附件/附件3/result2.xlsx` | XLSX模板 | Q2结果模板 | 是 | 否 | 10073 | `23b261b295c1b787d000eebbca6521c37075107b6fcf78724f8d395ce1798ff4` |
| ASSET-TPL-003 | `A题/附件/附件3/result3.xlsx` | XLSX模板 | Q3结果模板 | 是 | 否 | 9345 | `07e4793d620a7f899804c0298d49a16a197960440fd47f8bb780c57ec27e2859` |
| ASSET-TPL-004 | `A题/附件/附件3/result4.xlsx` | XLSX模板 | Q4结果模板 | 是 | 否 | 9351 | `86e9300ffa3d30c43de895ea6723da943e85b8740b137bcae5af7107f076eeac` |

## Workbook Structure

| Asset ID | Sheet 名称 | Skeleton Shape | Final Shape | Expansion Rule | Final Shape Status | 主要字段/结构 | 题面规定单位 | 备注 |
|---|---|---|---|---|---|---|---|---|
| ASSET-XLSX-001 | `Sheet1` | N/A | N/A | N/A | STATEMENT_FACT | 242 × 3；时间、温度、水分浓度 | 时间 `s`；温度 `°C`；水分浓度 `kg/kg` | 附件1，供Q1初期边界输入 |
| ASSET-XLSX-002 | `Sheet1` | N/A | N/A | N/A | STATEMENT_FACT | 146 × 2；时间、半径 | 时间 `s`；半径 `cm` | 附件2，供Q4尺寸变化输入 |
| ASSET-TPL-001 | `温度`、`水分浓度`；5 × 6 / Sheet | `TEMPLATE_SKELETON` | 题面约束已知，端点/计数待确认 | 时间每隔 `1 s` 至 `1800 s`；距离每隔 `0.1 cm` 至 `2 cm` | OPEN_QUESTION | A列时间；第1行到药材中心距离；示例列 `0, 0.1, 0.2, …, 2` | 时间 `s`；距离 `cm`；温度 `°C`；水分浓度 `kg/kg` | Q1官方空模板 |
| ASSET-TPL-002 | `温度`、`水分浓度`；5 × 6 / Sheet | `TEMPLATE_SKELETON` | 题面展示区间明确，完整矩阵端点/计数待确认 | 完整结果每隔 `1 s`；空间每隔 `0.1 cm`；展示表为3 h | OPEN_QUESTION | A列时间；第1行到药材中心距离；示例列 `0, 0.1, 0.2, …, 2` | 完整Excel时间 `s`；论文表时间 `h`；距离 `cm`；温度 `°C`；水分浓度 `kg/kg` | Q2官方空模板；设计 Gate 已核对 Sheet/轴/单位，未生成 Q2 结果 |
| ASSET-TPL-003 | `Sheet1`；5 × 6 | `TEMPLATE_SKELETON` | 烘干结束时间决定行数，待确认 | 时间每隔 `60 s`；距离每隔 `0.1 cm` | OPEN_QUESTION | A列时间；第1行到药材中心距离；示例列 `0, 0.1, 0.2, …, 2` | 时间 `s`；距离 `cm`；水分浓度 `kg/kg` | Q3官方空模板 |
| ASSET-TPL-004 | `Sheet1`；5 × 6 | `TEMPLATE_SKELETON` | 烘干结束时间、动态半径和表面列数待确认 | 时间每隔 `60 s`；空间每隔 `0.1 cm`，终点为药材表面 | OPEN_QUESTION | A列时间；第1行到药材中心距离；末列为“药材表面”示例 | 时间 `s`；距离 `cm`；水分浓度 `kg/kg` | Q4官方空模板 |

## Validation Baseline

由 `scripts/validate_inputs.py` 和 `scripts/validate_templates.py` 检查文件存在性、哈希、Sheet 名称、行列骨架、表头和模板数据区空白状态。校验脚本不计算题目答案、不调用求解器、不写入官方资产。

Q2 V3 补充：官方模板仍只读；V3 冻结的 candidate 规则为整数秒 `t=1..228536`、21 个半径，表头加数据区为 `228537 × 22 / Sheet`，t=0 只保留在 raw internal source。`deliverables/candidate/result2.xlsx` 已通过验证，仍须人工批准后才可进入 `deliverables/final/`。

V3 交付证据：`experiments/Q2_FREEZE_RUN_V3/`、`experiments/Q2_CANONICAL_DATA_MANIFEST.json`。官方模板 `A题/附件/附件3/result2.xlsx` SHA-256 保持 `23b261b295c1b787d000eebbca6521c37075107b6fcf78724f8d395ce1798ff4`。
