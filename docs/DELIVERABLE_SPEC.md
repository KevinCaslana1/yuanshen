# Deliverable Specification

> 本文件定义 result1.xlsx 至 result4.xlsx 的工程交付契约。它不包含预测值、模型公式、仿真结果或论文结论。

## Global Contract

- Official Source Root: `A题`
- Candidate Root: `deliverables/candidate`
- Final Root: `deliverables/final`
- Shape Policy: `TEMPLATE_SKELETON_IS_NOT_FINAL_OUTPUT_DIMENSION`
- Decimal Precision: `4`
- Contract Status: `OPEN_QUESTION`
- Official templates are read-only. Candidate and final files must be separate copies.

## result1.xlsx

- Official Template: `A题/附件/附件3/result1.xlsx`
- Candidate Path: `deliverables/candidate/result1.xlsx`
- Final Path: `deliverables/final/result1.xlsx`
- Sheet Name: `温度`, `水分浓度`
- Time Header: A列（时间）
- Time Unit: `s`
- Time Sampling Rule: `STATEMENT_FACT`，每隔 `1 s` 至 `1800 s`
- Spatial Header: 第1行（到药材中心的距离）
- Spatial Unit: `cm`
- Spatial Sampling Rule: `STATEMENT_FACT`，每隔 `0.1 cm`，题面范围至 `2 cm`
- Value Unit: `温度=°C`；`水分浓度=kg/kg`
- Decimal Precision: `4`
- Skeleton Shape: `[5, 6]` per sheet，标记为 `TEMPLATE_SKELETON`
- Expected Final Shape: `OPEN_QUESTION`；端点是否包含及最终行列计数待确认
- Expansion Rule: 按官方时间和空间采样规则展开模板，不把骨架尺寸当作最终尺寸
- Required Cells: 完整时间-空间结果矩阵及官方要求的表头
- Forbidden Changes: 修改官方模板；改变 Sheet 名称；覆盖 `A题/`；写入未验证的数值
- Validation Status: `OPEN_QUESTION`
- Open Questions: `OQ-001`

## result2.xlsx

- Official Template: `A题/附件/附件3/result2.xlsx`
- Candidate Path: `deliverables/candidate/result2.xlsx`
- Final Path: `deliverables/final/result2.xlsx`
- Sheet Name: `温度`, `水分浓度`
- Time Header: A列（时间）
- Time Unit: 完整 Excel 结果 `s`；论文展示表 `h`
- Time Sampling Rule: 完整结果每隔 `1 s`；完整时间范围和端点为 `OPEN_QUESTION`；论文展示每隔 `0.5 h` 至 `3 h`
- Spatial Header: 第1行（到药材中心的距离）
- Spatial Unit: `cm`
- Spatial Sampling Rule: 完整结果每隔 `0.1 cm`；论文展示距离 `0, 0.5, 1, 1.5, 2 cm`
- Value Unit: `温度=°C`；`水分浓度=kg/kg`
- Decimal Precision: `4`
- Skeleton Shape: `[5, 6]` per sheet，标记为 `TEMPLATE_SKELETON`
- Expected Final Shape: `OPEN_QUESTION`；完整时间范围与端点计数待确认
- Expansion Rule: 按官方完整结果采样规则展开模板；论文表与 Excel 的时间单位分开处理
- Required Cells: 两个官方 Sheet 的完整时间-空间结果矩阵及表头
- Forbidden Changes: 修改官方模板；改变 Sheet 名称；覆盖 `A题/`；把论文小时直接写入要求为秒的 A 列
- Validation Status: `OPEN_QUESTION`
- Open Questions: `OQ-001`, `OQ-002`

## result3.xlsx

- Official Template: `A题/附件/附件3/result3.xlsx`
- Candidate Path: `deliverables/candidate/result3.xlsx`
- Final Path: `deliverables/final/result3.xlsx`
- Sheet Name: `Sheet1`
- Time Header: A列（时间）
- Time Unit: 完整 Excel 结果 `s`；论文展示表 `h`
- Time Sampling Rule: 完整结果每隔 `60 s`；烘干结束时间决定最终范围；论文展示每隔 `6 h`
- Spatial Header: 第1行（到药材中心的距离）
- Spatial Unit: `cm`
- Spatial Sampling Rule: 完整结果每隔 `0.1 cm`；论文展示每隔 `0.5 cm`
- Value Unit: `kg/kg`
- Decimal Precision: `4`
- Skeleton Shape: `[5, 6]`，标记为 `TEMPLATE_SKELETON`
- Expected Final Shape: `OPEN_QUESTION`；结束时间行和最终行数待确认
- Expansion Rule: 按 `60 s` 与 `0.1 cm` 规则展开，结束时间由已确认的交付规则决定
- Required Cells: 水分浓度矩阵、时间列、距离表头和烘干结束时间行
- Forbidden Changes: 修改官方模板；改变 Sheet 名称；覆盖 `A题/`；在结束时间未确认前硬编码结束行
- Validation Status: `OPEN_QUESTION`
- Open Questions: `OQ-003`

## result4.xlsx

- Official Template: `A题/附件/附件3/result4.xlsx`
- Candidate Path: `deliverables/candidate/result4.xlsx`
- Final Path: `deliverables/final/result4.xlsx`
- Sheet Name: `Sheet1`
- Time Header: A列（时间）
- Time Unit: 完整 Excel 结果 `s`；论文展示表 `h`
- Time Sampling Rule: 完整结果每隔 `60 s`；烘干结束时间决定最终范围；论文展示每隔 `6 h`
- Spatial Header: 第1行（到药材中心的距离），终点为药材表面
- Spatial Unit: `cm`
- Spatial Sampling Rule: 完整结果每隔 `0.1 cm`；论文展示每隔 `0.5 cm`，终点为药材表面
- Value Unit: `kg/kg`
- Decimal Precision: `4`
- Skeleton Shape: `[5, 6]`，标记为 `TEMPLATE_SKELETON`
- Expected Final Shape: `OPEN_QUESTION`；动态半径、表面列数、结束时间和最终行数待确认
- Expansion Rule: 按 `60 s` 与动态空间范围规则展开，未经确认不得定义空间列数
- Required Cells: 水分浓度矩阵、时间列、距离表头、药材表面列和烘干结束时间行
- Forbidden Changes: 修改官方模板；改变 Sheet 名称；覆盖 `A题/`；未经确认写入固定空间终点
- Validation Status: `OPEN_QUESTION`
- Open Questions: `OQ-003`, `OQ-004`
