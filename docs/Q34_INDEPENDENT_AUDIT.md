# Q3/Q4 Independent Verification Audit

日期：2026-09-13
范围：只读复核冻结 Q2/Q3/Q4 资产，并以独立 FVM/BE/Picard 实现复核 Q3/Q4；不改写 `A题/`、`src/q2/` 或 final 数值工作簿。

## 结果摘要

| 项目 | 结果 | 状态 |
|---|---:|---|
| Q3 冻结 raw 全时域扫描 | last fail `206935 s`, `Cmax=0.1500000658293865`；first strict pass `206936 s`, `Cmax=0.14999977460230157`；critical `r=0` | PASS |
| Q3 独立局部细化 | `n=20` 与 `n=40`、`dt=1/1024 s` 的连续 crossing 分别为 `206935.2260985608 s` 与 `206935.11305949945 s`；四位小时值均 `57.4820 h` | PASS |
| Q4 独立生产复现 | 独立 `n=96, dt=4 s` 得 `53.082703798850744 h`，与冻结 `53.08270378038297 h` 相差约 `6.65e-5 s` | PASS（复现） |
| Q4 独立精化 | 独立 `n=144, dt=2 s` 得 `52.830168163752184 h`，四位值 `52.8302 h`，未与 `53.0827 h` 稳定 | HOLD |
| Q4 恒半径回归 | 独立 moving-coordinate 与 fixed-radius solver 在 `60/600/3600/7200 s` 的温度/水分最大差均为 `0` | PASS |
| Q4 守恒精化 | 最大逐步残差随 `48/8 → 96/4 → 144/2` 为 `8.3088e-4 → 4.1470e-4 → 2.0895e-4`；但事件时刻仍未稳定 | SUPPORTING, not sufficient |
| Q4 Table6 表面/外域 | 全部矩阵行无外域非空值，表面列完整 | PASS |

## 解释边界

Q3 独立核验通过，推荐纸面时间为 `57.4820 h`。Q4 的 frozen numerical artifact 保留原值 `53.08270378038297 h`（`191097.7336093787 s`），但本次精化独立核验为 HOLD；不得把 Q4 `53.0827 h` 写成已经通过精化收敛证据，也不得用 `52.8302 h` 自动替换 final。

外部截图仅作 `EXTERNAL_REFERENCE`：冻结 Q3 相对 `57.46681156 h` 高 `0.01519581847222895 h`；冻结 Q4 相对 `51.0823 h` 高 `2.00040378038297 h`。没有进行任何参数、单位、插值或事件阈值调参来贴合截图。

Q4 附录 4 公式、`xi=r/R(t)` 变换、`Rdot/R` 符号、圆柱 `1/r` 几何、变量 `k/D`、Robin 边界、动态控制体积和 Attachment 2 尾段在独立方程审计中均为 `MATCH`；但这不能抵消网格/时间精化未稳定这一关键阻断项。

## 证据文件

- `experiments/Q34_INDEPENDENT_AUDIT/audit.json`
- `experiments/Q34_INDEPENDENT_AUDIT/Q3_LOCAL_REFINEMENT.csv`
- `experiments/Q34_INDEPENDENT_AUDIT/Q4_CONVERGENCE.csv`
- `experiments/Q34_INDEPENDENT_AUDIT/Q4_RADIUS_COMPARISON.csv`
- `experiments/Q34_INDEPENDENT_AUDIT/Q4_MOVING_DOMAIN_EQUATION_AUDIT.md`
- `scripts/run_q34_independent_audit.py`

冻结 `deliverables/final/result3.xlsx` 和 `deliverables/final/result4.xlsx` 的 SHA-256 在审计前后均保持原登记值；没有生成 candidate replacement。

## 决策

```text
Q3 INDEPENDENT VERIFICATION = PASS
Q4 INDEPENDENT VERIFICATION = HOLD / HUMAN REVIEW
Q3 FROZEN RESULT = CONFIRMED
Q4 FROZEN NUMERICAL ARTIFACT = UNCHANGED, NOT RE-CERTIFIED FOR PAPER
```
