# Q4 Final Asymptotic Certification Audit

日期：2026-09-13

## 结论

`Q4 FINAL NUMERICAL CERTIFICATION = HOLD`。本轮完成 gate 指定的最后空间 full run `n=512, dt=2 s` 和唯一时间验证 `n=384, dt=1 s`，但空间外推方法包络加最后细网格到连续极限的关系仍给出约 `0.0162450695 h` 的保守空间不确定度，约 `58.48 s`，高于 PCHIP/linear 建模敏感性 `21.7324 s`。因此不生成 `deliverables/candidate_reaudit/result4.xlsx`，不覆盖历史 final。

禁止事项均已遵守：未重审 PDE、Appendix 4、Q1/Q2/Q3、表 1–5；未以外部 `51.0823 h` 调参；未运行 `n=640` 或 `dt=0.5 s`。

## n=512 spatial run

`n=512, dt=2 s` 从 `t=0` 独立运行，未使用 checkpoint 或旧网格状态：

- `t4=189614.85238398053 s=52.67079232888348 h`
- `R(t4)=1.2 cm`
- controlling point：center / `ξ=0`
- root bracket width：`0.0625 s`
- runtime：`804.4838 s`
- max step mass residual：`2.0650105661e-4`
- max Robin residual：`7.7928124776e-7`
- max Picard：`6`

空间序列全部固定 `dt=2 s`：`n=96/144/192/256/320/384/512`，事件时刻保持单调下降，质量残差总体改善，Robin 残差总体下降。

## Spatial asymptotic fits

空间拟合使用非等比网格直接拟合，不使用等比 Richardson 简化式。

### Method A: free-p

模型为 `t(n)=t_inf+a*n^(-p)`：

| 网格 | p | t_inf / h | max fit residual / s |
|---|---:|---:|---:|
| `[192,256,320,384,512]` | 2.1329581337 | 52.6595573001 | 0.2007 |
| `[256,320,384,512]` | 2.1031763600 | 52.6592231593 | 0.0432 |

### Method B: fixed p=2

| 网格 | t_inf / h | max fit residual / s |
|---|---:|---:|
| `[320,384,512]` | 52.6582477343 | 0.2281 |
| `[256,320,384,512]` | 52.6578957005 | 0.6510 |
| `[192,256,320,384,512]` | 52.6570522797 | 2.3758 |

### Method C: p=2 plus n^-3 correction

| 网格 | t_inf / h | max fit residual / s |
|---|---:|---:|
| `[256,320,384,512]` | 52.6588571833 | 0.0149 |
| `[192,256,320,384,512]` | 52.6589347562 | 0.0576 |

七个合理估计的中心取中位数：

- spatial dt=2 continuum estimate：`52.6588571833 h`
- method envelope：`0.0025050204 h=9.0181 s`
- n=512 finite-grid 到 continuum 最大关系：`0.0137400491 h=49.4642 s`
- conservative spatial uncertainty：`0.0162450695 h=58.4823 s`

自由阶范围为 `2.0000–2.1330`，free-p 末端估计从 `2.13296` 到 `2.10318`，仍有漂移；不能把零残差的三点拟合误写成高精度证据。

## Temporal verification

在 `n=384` 上，已有 H (`dt=2 s`) 与新 J (`dt=1 s`) 均从 `t=0` 独立运行：

- `t_dt2=52.6804294113 h`
- `t_dt1=52.6797622096 h`
- `dt2→dt1=-2.4019260 s`
- 历史 `n=144,dt4→dt2=-4.8060737 s`
- supporting observed order `q=1.0006671`
- 方向一致，支持 Backward Euler 一阶时间趋势
- 一阶时间外推 `t_dt0(n=384)=52.6790950079 h`
- `dt=2→dt=0` 修正：`-4.8038520 s`
- conservative temporal uncertainty：`0.0006672017 h=2.4019 s`

空间极限没有稳定前，不进行大规模二维参数矩阵；最终 audit estimate 将空间 dt=2 极限加上该一阶时间修正：

```text
t4_star = 189567.08200778931 s
t4_star = 52.65752277994147 h
paper-format display = 52.6575 h
```

该值是连续极限审计估计，不是已写入 workbook 的 production field value。

## Uncertainty and comparison

- spatial discretization：`0.0162450695 h`
- temporal discretization：`0.0006672017 h`
- root location：`0.0000173611 h` (`0.0625 s`)
- conservative numerical total：`0.0169296323 h=60.9467 s`
- PCHIP/linear：`21.7324 s`，单列为 `MODELING / INTERPOLATION SENSITIVITY`
- `R(t4)=1.2 cm`，controlling point 为 center / `ξ=0`
- 相对旧冻结 `53.0827 h`：`-0.4251810004 h`
- 相对外部 `51.0823 h`：`+1.5752227799 h`

外部值未进入 fit、objective、parameter tuning 或 acceptance rule。当前数值不确定度约 `60.95 s`，高于插值敏感性约 `21.73 s`，且空间阶仍有漂移，故不能认证 PASS。

## Delivery decision

- `deliverables/final/result4.xlsx`：保持历史冻结，不修改
- Q4 manifest、Table6、Q4 figures、comparison figure：均不修改
- `deliverables/candidate_reaudit/result4.xlsx`：未创建
- `docs/Q4_CORRECTED_RESULT_AUDIT.md`：未创建，因为认证未 PASS
- 不自动运行 `n=640`；停止自动细化，等待人工决定

机器可读证据：

- `experiments/Q4_SPATIAL_CONVERGENCE_FINAL/q4_final_asymptotic_spatial_estimates.json`
- `experiments/Q4_SPATIAL_CONVERGENCE_FINAL/spatial_run_I_n512_dt2.json`
- `experiments/Q4_FINAL_ASYMPTOTIC_CERTIFICATION/temporal_run_J_n384_dt1.json`
- `experiments/Q4_FINAL_ASYMPTOTIC_CERTIFICATION/q4_final_asymptotic_certification.json`

```text
Q4 FINAL NUMERICAL CERTIFICATION = HOLD
DO NOT MODIFY FINAL RESULT4
STOP AUTOMATIC REFINEMENT
```
