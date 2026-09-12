# Q3 Final Freeze Audit

日期：2026-09-12
状态：`FINAL FREEZE COMPLETE / APPROVED`

## Threshold event

判定条件为全径向节点满足 `max_r C(r,t) < 0.15 kg/kg`。冻结证据复用已验证 Q3 candidate，不重跑全程 solver：

| 项目 | 结果 |
|---|---:|
| 粗事件区间 | `[206935.0, 206936.0] s` |
| `t_before` / `max C` | `206935.0 s` / `0.1500000658293865` |
| `t_after` / `max C` | `206936.0 s` / `0.14999977460230157` |
| 局部细化方法 | BE/Picard continuation，`1024` substeps/s |
| 最终局部 bracket | `[206935.2255859375, 206935.2265625] s` |
| 事件时间不确定度 | `0.0009765625 s`（最终 bracket 宽度） |
| 冻结烘干时间 | `206935.2265625 s = 57.482007378472225 h` |
| 临界半径 | `r=0.0 cm` |
| endpoint `max C` | `0.14999999986492263` |
| threshold proof | `PASS` |

## Workbook

- 来源：冻结 Q2 raw official lattice，source trace `3448/3448`。
- `deliverables/candidate/result3.xlsx` → `deliverables/final/result3.xlsx` 为字节原样复制。
- candidate/final SHA-256：`08c67308b9b0e67cde2911dd4b701f12c4c024720ad257314bdf16a31d480461`。
- 形状：`3449 × 22`，单表；时间为严格 `60 s` lattice，`60..206880 s`。
- 无公式、无 NaN/Inf、数值格式四位小数；精确事件时刻未写入官方 workbook，仅用于论文表和本审计。

## Paper assets

- Table 5：`deliverables/final/paper/tables/table5_q3.csv/.md/.xlsx`，trace `77/77`。
- Q3 figures：3 组 PNG/SVG，PNG ≥300 DPI，figure trace `3/3`。
- 总资产登记：`deliverables/final/paper/PAPER_ASSET_MANIFEST.json`。
- 最终清单：`deliverables/final/Q3_MANIFEST.json`。

未修改 Q1/Q2、官方源、`src/q1/` 或 `src/q2/`；本次冻结未 push 远程。
