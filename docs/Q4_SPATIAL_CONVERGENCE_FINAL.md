# Q4 Spatial Convergence Extrapolation Audit

日期：2026-09-13

## 结论

`Q4 CONTINUUM CONVERGENCE = HOLD`。本轮按人工 gate 完成 `n=256` 和 `n=320` 的 fresh-from-`t=0` 空间细化，并按要求追加 `n=384`；不覆盖历史 `result4.xlsx`、Q4 manifest、Table6 或 Q4 图表，也不创建 corrected candidate。

所有空间运行固定 `dt=2 s`，使用已审计的独立 FVM/Backward Euler/Picard 实现，禁止 checkpoint、E 状态续算和临界窗口短跑。外推使用非等比网格的直接三参数模型：

```text
t(n) = t_inf + a * n^(-p)
```

不使用只适用于固定 refinement ratio 的简化 Richardson 公式。

## Spatial runs

| Run | n | dt (s) | t4 (s) | t4 (h) | R(t4) (cm) | controlling point | runtime (s) |
|---|---:|---:|---:|---:|---:|---|---:|
| B | 96 | 2 | 191092.92436837355 | 53.08136788010376 | 1.2 | center / ξ=0 | 157.2324 |
| D | 144 | 2 | 190188.60538950787 | 52.830168163752184 | 1.2 | center / ξ=0 | 215.5113 |
| E | 192 | 2 | 189903.26003601108 | 52.75090556555863 | 1.2 | center / ξ=0 | 301.6297 |
| F | 256 | 2 | 189752.21918926245 | 52.70894977479512 | 1.2 | center / ξ=0 | 345.4672 |
| G | 320 | 2 | 189685.12377940913 | 52.69031216094698 | 1.2 | center / ξ=0 | 417.7388 |
| H | 384 | 2 | 189649.54588051673 | 52.68042941125465 | 1.2 | center / ξ=0 | 512.7533 |

F/G/H 均为完整 fresh `t=0` 运行，局部 root bracket 宽度均为 `0.0625 s`。F/G/H 最大 Picard 次数均为 `5`；最大逐步质量残差分别为 `2.0712223131e-4`、`2.0675035602e-4`、`2.0658233091e-4`，最大 Robin 残差分别为 `1.2874205417e-6`、`1.1181288028e-6`、`9.8094208296e-7`，未见随网格加密恶化。

## Triplet extrapolation

| Triplet | p | t_inf (s) | t_inf (h) | max fit residual (s) |
|---|---:|---:|---:|---:|
| [96, 144, 192] | 2.2872370118 | 189596.74062362823 | 52.66576128434117 | 0 |
| [144, 192, 256] | 2.2112949180 | 189582.3564055115 | 52.66176566819764 | 0 |
| [192, 256, 320] | 2.1574210187 | 189576.61873040695 | 52.66017186955749 | 0 |
| [256, 320, 384] | 2.1173963902 | 189574.0336015354 | 52.65945377820427 | 0 |

每个 triplet 恰有三个数据点和三个拟合参数，因此拟合残差为一致性检查，不能单独作为不确定度证明。空间极限稳定性使用相邻 triplet 的 `t_inf` 差值：

- Triplet 1 → 2：`0.0039956161 h`
- Triplet 2 → 3：`0.0015937986 h`
- Triplet 3 → 4：`0.0007180914 h`（约 `2.5851 s`）

最近两组极限仍大于 `0.00005 h`；`p` 从 `2.2872` 逐步变为 `2.1174`，尚未达到可声明稳定的状态。趋势接近二阶但仍有可见漂移，不能据此进行 Richardson 外推或生成连续极限 final 值。

## Temporal verification

暂缓 `dt=1 s`。此前 A/B 与 C/D 的时间贡献约 `0.001335 h`，但空间外推极限尚未稳定，先进行时间 Richardson 会把尚未消除的空间变化混入二维极限估计。待空间极限稳定后，才在一个最终高网格上比较 `dt=2/1 s`。

## Uncertainty and sensitivities

当前空间外推稳定性不确定度取最近两个 triplet 极限差：`0.0007180914 h`，超过目标 `0.00005 h`。事件 root 局部分辨率为 `0.0625 s = 0.0000173611 h`，与场离散误差分开记录。PCHIP/linear 半径敏感性沿用既有一次检查：差异 `21.7324270 s = 0.0060367853 h`，属于模型/插值敏感性，不作为空间离散误差；生产插值仍保留 PCHIP。

## Comparisons and delivery decision

最新外推值 `52.6594537782 h` 相比历史冻结 `53.0827037804 h` 差 `-0.4232500022 h`；相比外部参考 `51.0823 h` 差 `+1.5771537782 h`。外部值不进入拟合、目标函数、调参或验收规则；由于当前外推尚未收敛，不能对外部值作模型判断。

```text
Q4 CONTINUUM CONVERGENCE = HOLD
DO NOT MODIFY FINAL RESULT4
DO NOT CREATE CORRECTED CANDIDATE
```

证据目录：`experiments/Q4_SPATIAL_CONVERGENCE_FINAL/`。机器可读记录：`spatial_run_F_n256_dt2.json`、`spatial_run_G_n320_dt2.json`、`spatial_run_H_n384_dt2.json`、`spatial_continuum_fits.json`。
