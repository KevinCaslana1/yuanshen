# Q4 Final Freeze Audit

日期：2026-09-12
状态：`FINAL FREEZE COMPLETE / APPROVED`

## Threshold event

判定条件为移动域内全材料坐标满足 `max C(r,t) < 0.15 kg/kg`。冻结证据复用已验证 Q4 candidate，不重跑全程 solver：

| 项目 | 结果 |
|---|---:|
| 粗事件区间 | `[191096.0, 191100.0] s` |
| `t_before` / `max C` | `191096.0 s` / `0.15000087683231333` |
| `t_after` / `max C` | `191100.0 s` / `0.14999885377291058` |
| 局部细化方法 | BE/Picard local refinement，`64` substeps over coarse bracket |
| 事件时间不确定度 | `0.0625 s`（`4/64 s` 局部细化分辨率） |
| 冻结烘干时间 | `191097.7336093787 s = 53.08270378038297 h` |
| `R(t4)` | `1.2 cm` |
| 临界材料坐标 | `ξ=0.0`，`r=0.0 cm` |
| endpoint `max C` | `0.14999999999999525` |
| threshold proof | `PASS` |

## Moving-domain audit

- 半径来源：`A题/附件/附件2.xlsx`，SHA-256 `5563acbfa4b4afb10cc6c03e2207e5369bf39da27576672aff14cc5c32e704af`。
- 插值：单调 PCHIP-compatible Fritsch–Carlson；节点最大误差 `0`。
- `r > R(t)` 的固定物理位置保持 blank/unavailable；无外推、填零、复制表面值或最近邻伪填充；违规数 `0`。
- Table 6“药材表面”使用模型实际移动表面值 `C(R(t),t)`，不是最近固定网格点。
- 最大归一化质量守恒逐步残差：`3.4553928505477293e-4`；最大 Robin 通量差：`4.5474756348265686e-7`。

## Workbook

- `deliverables/candidate/result4.xlsx` → `deliverables/final/result4.xlsx` 为字节原样复制。
- candidate/final SHA-256：`dc6897a80b71577cbcef082d31cf884285f8858f1e1ca8fd613b04feba480586`。
- 形状：`3185 × 22`，单表；时间为严格 `60 s` lattice，`60..191040 s`。
- 无公式、无 NaN/Inf、数值格式四位小数；精确事件时刻未写入官方 workbook，仅用于论文表和本审计。

## Paper assets

- Table 6：`deliverables/final/paper/tables/table6_q4.csv/.md/.xlsx`，trace `90/90`。
- Q4 figures：3 组 PNG/SVG，PNG ≥300 DPI，figure trace `4/4`。
- 对比图：`fig_5_18_q3_q4_drying_time_comparison`，trace `1/1`。
- 总资产登记：`deliverables/final/paper/PAPER_ASSET_MANIFEST.json`。
- 最终清单：`deliverables/final/Q4_MANIFEST.json`。

Q3/Q4 时间差仅作为数值差异报告：`Q4-Q3 = -15837.492953121313 s`，相对差 `-0.07653357630890342`；不据此单独宣称“收缩使烘干加快”，因为几何和附录物性同时变化。
