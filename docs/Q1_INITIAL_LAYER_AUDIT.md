# Q1 Initial-Layer & Surface-Accuracy Audit

日期：2026-09-11  
范围：仅 Q1；只生成并审计 candidate `result1.xlsx`，不写入 `deliverables/final/`；不修改 `A题/`、官方初始条件或官方输入。
初始层诊断提交：`3b0785a6ff5bf0f3e2a27845c6707d0b98b7bb13`；冻结运行代码提交：`a40ca42`

## 后续全时域复验结论（2026-09-11）

本文件前述“尚未完成全时域验证”的状态已由后续实验关闭：`EXP-Q1-FULL-SPATIAL`、`EXP-Q1-FULL-TEMPORAL` 和 `Q1_FREEZE_RUN` 完成并通过。生产配置冻结为边界聚簇保守 FVM（`cluster_power=2`、base320 请求网格/实际338区间）、首步 BE 后固定步长 BDF2 `dt=0.25 s`。候选 `deliverables/candidate/result1.xlsx` 已从 `Q1_FREEZE_RUN/run_1` 生成并通过验证；`deliverables/final/` 仍等待人工批准，Q2 不启动。

## Current Project Status

- 当前阶段：`Q1 FULL-HORIZON PRODUCTION CONFIG FREEZE & CANDIDATE DELIVERABLE GATE`。
- Q1 的 M1/BE 仍作为可追溯均匀网格参考；边界聚类保守 FVM（聚类幂 `p=2`、显式保留全部官方输出节点）已通过全时段验证并冻结为生产候选。
- 温度初始场与温度 Robin 表示相容；均匀初始水分场与表面水分 Robin 条件不相容，且短时表面误差随时间衰减，支持 `H-Q1-INITIAL-LAYER`。
- 当前 gate 结论：`Q1 RESULT & DELIVERABLE GATE COMPLETE / WAITING FOR HUMAN Q1 FREEZE APPROVAL`。候选已验证，最终目录仍为空。

## Compatibility Analysis

### temperature

在 `t=0`，`T∞(0)=28 °C`，内部初温为 `28 °C`，初始径向梯度为 0。按当前 Robin 表示计算的残差为 `-0.0 W/m²`，记为 `COMPATIBLE_WITHIN_REPRESENTATION`。

### moisture

在 `t=0`，`C∞(0)=0.01963 kg/kg`，内部初始含水率为 `2.55 kg/kg`，`D(C0)=4.9376550942e-9 m²/s`。初始水分跳跃为 `2.53037 kg/kg`，Robin 残差为 `-2.024296e-6 m/s`，对应外向通量为 `+2.024296e-6 m/s`，记为 `INCOMPATIBLE_INITIAL_TRACE`。

这只支持一个数值诊断假设，不表示模型错误；本轮没有修改初始场、`hm` 口径或边界类型。

## Initial Layer Evidence

`EXP-Q1-INITIAL-LAYER` 在 0–10 s 诊断中观察到均匀网格 N1280、`dt=0.015625 s` 的 t=1 s 表面 Richardson 剩余约 `8.7151e-5 kg/kg`；r=1.975 cm 的剩余约 `1.4384e-5 kg/kg`，r=1.95 cm 已降至 `6.26e-9 kg/kg`，误差集中在表面薄层。

`EXP-Q1-SURFACE-DECAY` 固定 `dt=0.0625 s` 比较均匀 N640→N1280：r=2.0 cm 的空间差从 t=1 s 的 `3.0796268e-4 kg/kg` 降到 t=100 s 的 `2.1779886e-5 kg/kg`，比值约 `14.14`；后期观测阶约为 2。该趋势与短时初始层解释一致。

登记用语：

> 当前数值困难主要由初始水分场与表面 Robin 条件不相容产生的短时表面边界层导致。

## Early-Time Spatial Convergence

均匀 M1、共同 `dt=0.03125 s` 的早期空间梯在 t=1 s 表面仍给出约 `8.7e-5 kg/kg` 的保守剩余；聚类候选在共同 `dt=0.0625 s` 下将真实 Q1 的 base640→base1280 t=1 s 表面差降至 `3.6752550e-6 kg/kg`。独立聚类 benchmark 的空间 L∞ 观测阶为 `1.9481、1.9658、1.9635`。

## Early-Time Temporal Convergence

聚类 base1280 t=1 s 表面值为：

| dt (s) | C(R,1s) (kg/kg) |
|---:|---:|
| 0.0625 | 2.5179803597 |
| 0.03125 | 2.5178539408 |
| 0.015625 | 2.5177905315 |
| 0.0078125 | 2.5177587784 |

`dt=0.03125→0.015625 s` 与 `0.015625→0.0078125 s` 的表面观测阶为 `0.9978`，Richardson 剩余估计为 `3.1850238e-5 kg/kg`。因此表面 t=1 s 仍是舍入认证的主限制。

## BDF2 Startup Comparison

在 N640、正常步长 `0.25 s` 下，比较标准“首步 BE、随后 BDF2”和 0–1 s BE 子步后重启 BDF2：启动子步 `.25/.125/.0625 s` 的标准/早期最大差异分别为 `9.3725e-4`、`9.9496e-4`、`1.5769e-3 kg/kg`。早期子步没有表现出相对标准启动的稳定改善，故不将其冻结为生产策略。

## Surface Error Decay

误差曲线见 `experiments/EXP-Q1-SURFACE-DECAY/surface_moisture_error_decay.svg`。曲线使用 N640→N1280、共同 `dt=0.0625 s` 的空间差，分别绘制 r=1.9 cm 和 r=2.0 cm，时间范围 1–100 s。r=2.0 cm 从早期峰值持续衰减；r=1.9 cm 在 t=1 s 已接近机器精度，随后随着边界层向内传播才出现可见差异。

## Uniform vs Boundary-Clustered Grid

边界聚类候选使用 `r=R[1-(1-x)^2]` 的非均匀节点映射，并将 `0,0.001,...,0.020 m` 显式并入节点集合。非均匀保守装配包含中心半体积、内部面通量和表面 Robin 半体积。

制造解 benchmark：空间 L∞ 观测阶约 `1.95–1.96`，时间 L∞ 观测阶约 `1.01–1.06`。真实 Q1 短时空间对照：

| 比较 | t=1 s、r=2.0 cm 差异 (kg/kg) |
|---|---:|
| 均匀 N320→N640 | `1.3890949e-3` |
| 聚类 base640→base1280 | `3.6752550e-6` |

跨均匀/聚类网格族的差异不作为误差估计，只用于候选行为对照。

## Reference Solution

聚类 base1280、`dt=0.0078125 s` 的短时参考为：

- `C(R,1s) = 2.5177587784 kg/kg`；
- 空间 Richardson 剩余约 `1.2259e-6 kg/kg`；
- 时间 Richardson 剩余约 `3.1850e-5 kg/kg`；
- 当前保守合成不确定度取最大值：`3.1850e-5 kg/kg`。

这是 Q1 t=1 s 的候选参考，不是已批准写入官方结果文件的最终值。

## Rounding Certification

以四位小数、`ROUND_HALF_UP` 的半单位阈值为判据，使用 t=1 s 聚类 base1280 最细参考值，并对每个官方位置取空间/时间 Richardson 剩余误差的最大值作为保守不确定度：

- `ROUNDING_CERTIFIED`: `20/21`；
- `ROUNDING_AMBIGUOUS`: `1/21`；
- 歧义位置：`r=2.0000 cm`，参考值 `2.5177587784 kg/kg`，不确定度 `3.1850e-5 kg/kg`，距最近四位小数半单位阈值约 `8.778e-6 kg/kg`。

完整逐位置数据见 `experiments/EXP-Q1-CLUSTER-TEMPORAL/metrics.json` 的 `reference_t1_official_values`。

## Recommended Production Strategy

以下历史建议已由后续全时段验证和 `Q1_FREEZE_RUN` 落实为冻结生产配置：

1. 保持 M1 物理方程、Robin 边界和官方初始水分场不变。
2. 已采用显式保留官方输出节点的边界聚类保守 FVM，并完成 0–1800 s 全网格复验。
3. 已冻结标准首步 BE、随后固定步长 BDF2；未经全时段证据支持的早期子步切换不进入生产配置。
4. 全网格 raw、Richardson、守恒/范围、辅助舍入诊断和双次冻结复跑均通过；候选已生成，最终目录仍等待人工确认。

## Validation Summary

| Item | Result |
|---|---|
| t=0 temperature compatibility | PASS within representation |
| t=0 moisture compatibility | Initial-layer mismatch supported |
| surface error decay | PASS as diagnosis |
| BDF2 startup comparison | Completed; early substeps not selected |
| clustered manufactured benchmark | PASS |
| clustered real-Q1 short comparison | PASS as candidate evidence |
| t=1 reference | Historical short-time diagnostic; superseded by full-horizon freeze evidence |
| rounding certification | Auxiliary only; full-horizon ambiguity does not auto-fail |
| full 0–1800 s candidate verification | PASS |
| candidate/final workbook | candidate PASS / final pending human approval |
| Q2/Q3/Q4 | NOT STARTED |

## Remaining Risks

- 候选已在完整 `1..1800 s × 0.0..2.0 cm` 网格完成原始值、Richardson、守恒、范围和辅助舍入诊断；当前不确定度满足团队数值门。
- 短时 t=1 s 表面歧义属于舍入辅助诊断，不构成自动失败；不得把该短时参考单独当作最终交付值。
- 生产配置已完成双次从零冻结复跑并通过确定性检查；最终目录复制仍需人工批准。
- `A-Q1-001` 一维径向假设、`A-Q1-005` Robin 建模口径和 `A-Q1-006` 物理简化仍按项目账本管理；本轮不重开这些物理决策。

## Git Status

- 初始层诊断提交：`3b0785a6ff5bf0f3e2a27845c6707d0b98b7bb13`；冻结运行代码提交：`a40ca42`。
- 全时段实验、冻结运行和候选追溯均已记录在对应实验目录，官方源 `A题/` 未修改。
- 本轮按授权只做本地提交，不推送 GitHub。

## Commit SHA

`a40ca42`（Q1 冻结运行代码提交；后续文档提交将更新交接记录）

结论：`Q1 RESULT & DELIVERABLE GATE COMPLETE`；`WAITING FOR HUMAN Q1 FREEZE APPROVAL`；`DO NOT START Q2`。
