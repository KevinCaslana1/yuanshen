# Q2 Production Freeze Run

日期：2026-09-12

## Scope

本目录记录人工批准的 Q2 production freeze 双跑、独立时间/空间精度确认和完整 lineage。正式生产来源固定为 `run_1`；`run_2` 只用于确定性复核；旧的 Q2 validation/recovered/interrupted/duplicate 产物不作为正式来源。

## Frozen configuration

- Candidate A：边界聚簇保守有限体积法；实际 98 cells / 99 nodes；`cluster_power=2`。
- `dt=0.25 s`；首步 Backward Euler，随后 BDF2；coupled temperature-moisture Picard。
- `linear` interpolation；harmonic interface mean；`h=25 W/(m²·K)`、`hm=8e-7 m/s` 作为 carried-forward modeling assumptions。
- Attachment 1 在 `0..14400 s` 分段线性；`t>14400 s` 使用 `T_inf=49.99525 °C`、`C_inf=0.049988 kg/kg`，不平滑。
- 被动 `max(C)-0.15` 只用于方向性首次穿越观察；发现 bracket `[207034.5, 207034.75] s`，生产时域为 `ceil(t_high)+21600=228635 s`。

## Production outcome

Run1/Run2 均从 `t=0` 新鲜启动，推进到 `228635 s`，raw/sampled/diagnostics/checkpoint 均 byte/hash identical。生产场值、Picard、属性范围、质量/热量/Robin、中心对称和有限性检查通过；这些结果不等于精度门通过。

独立参考组为同一代码和输入下的 `dt=0.125 s`、`dt=0.5 s` 和 `n_intervals=160`。`accuracy_confirmation.json` 的正式输出区域估计为：温度 L∞ `1.9082196854469657e-4 °C`、L2 RMS `4.400124076121024e-6 °C`；水分 L∞ `2.0357404664261836e-4 kg/kg`、L2 RMS `3.0182278875418313e-5 kg/kg`。因此 accuracy gate 为 `FAIL`，候选工作簿和 Q2 正式图表生成按 fail-closed 规则未执行。

## Diagnosis

Attachment 1 在 `14400 s` 的 raw 值为 `(50.165, 0.04986)`，而 `14400 s+epsilon` 的冻结 post-attachment 值为 `(49.99525, 0.049988)`，输入跳变为 `(-0.16975, +0.000128)`。最大 temporal temperature difference 出现在 `t=14401 s, r=2.0 cm`；最大 spatial moisture difference 出现在 `t=1 s, r=2.0 cm`。这两个峰分别对应 post-attachment input jump 和初始表面层离散误差，不能写成模型精度或物理优越性证据。

## Reproduction

```powershell
.\\.venv\\Scripts\\python.exe scripts\\run_q2_production_freeze.py
.\\.venv\\Scripts\\python.exe scripts\\run_q2_accuracy_confirmation.py
```

以上命令会重新创建同名 production/accuracy 目录，因此本目录当前产物应被视为本次唯一正式审计记录；候选 `result2.xlsx` 尚未生成。
