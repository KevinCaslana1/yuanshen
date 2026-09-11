# Experiments Index

本文件只保存正式实验的索引和关键结果；每个实验的详细配置与产物放在 `experiments/EXP-xxx/`。

## 实验索引

| ID | Question | Model | Purpose | Key Config | Metrics | Status | Evidence |
|---|---|---|---|---|---|---|---|
| EXP-001 | Q1 | M1 smoke | 检查输入、插值、单位、边界方向和最小离散 | 10 s、N=8、附件1原始点 | 所有运行检查通过，Picard max=2 | COMPLETED | `experiments/EXP-001/` |
| EXP-002 | Q1 | B0 vs M1 vs M2 | 比较均匀 Baseline、非线性径向和常-D径向模型 | 1800 s、dt=1 s、N=80 | M1/M2验证通过；平均响应与径向差异已记录 | COMPLETED | `experiments/EXP-002/` |
| EXP-003 | Q1 | M1 | 时间离散敏感性与收敛 | `dt=1/0.5/0.25 s` | 1→0.5 s最大差异 `0.000600 K/4.40e-5 kg/kg`；0.5→0.25 s进一步减半 | COMPLETED | `experiments/EXP-003/` |
| EXP-004 | Q1 | M1 | 空间网格收敛 | `N=40/80/160`，`dr=0.5/0.25/0.125 mm` | 80→160最大差异 `1.33e-5 K/1.41e-4 kg/kg` | COMPLETED | `experiments/EXP-004/` |
| EXP-005 | Q1 | M1 vs M3 | Robin 与 Dirichlet 边界敏感性 | 相同输入、dt=1 s、N=80 | 最大差异 `4.727 K/1.477 kg/kg`；Robin验证通过 | COMPLETED | `experiments/EXP-005/` |
| EXP-006 | Q1 | M1 | 分段线性与零阶保持输入敏感性 | 同一附件1原始点、dt=1 s、N=80 | 最大差异 `0.178 K/1.02e-4 kg/kg`；两种运行检查通过 | COMPLETED | `experiments/EXP-006/` |
| EXP-007 | Q1 | M1 | 通量、储量和物理范围 sanity check | 1800 s、dt=1 s、N=80 | 质量残差 `-5.42e-20`，能量残差 `1.13e-7`，范围有限 | COMPLETED | `experiments/EXP-007/` |
| EXP-Q1-FINAL-CONV | Q1 | M1 | 最终交付网格的原始值与四位小数输出级收敛 | 空间 N=80/160/320、固定 dt=0.25 s；时间 dt=1/0.5/0.25 s、固定 N=320；完整 1800×21 网格及论文 7×5 点 | N160→N320 与 dt1→dt0.25 均存在四位小数差异；不得生成候选文件 | BLOCKED | `experiments/EXP-Q1-FINAL-CONV/` |
| EXP-Q1-NUM-BENCH | Q1 | Isolated FVM benchmark | 用制造解验证径向 FVM、中心/Robin 边界、空间与时间阶；不使用生产输入 | `u=e^{-t}(1+r^4)`；N=40/80/160/320；BE 时间细化；附加 BDF2 对照 | BE 空间 L∞ 阶约 `1.97–2.00`，BE 时间阶约 `0.99–1.01`；BDF2 首个细化 L∞ 阶 `1.99` | COMPLETED | `experiments/EXP-Q1-NUM-BENCH/` |
| EXP-Q1-NUM-DIAG | Q1 | M1 | 对相同物理时刻/位置执行 Level 1–3 收敛诊断、Richardson 估计和误差定位 | N=80/160/320、dt=1/0.5/0.25 s；完整 1800×21 及论文 7×5 | 空间温度阶约 `2`；BE 时间阶约 `1`；水分误差集中早期/表面；完整网格仍未满足估计误差门 | COMPLETED | `experiments/EXP-Q1-NUM-DIAG/` |
| EXP-Q1-PICARD-SENS | Q1 | M1 | 检查 Picard 容差 `1e-6/1e-8/1e-10` 对场值和迭代次数的影响 | 300 s、N=160、dt=0.25 s | 温度差为 `0`；含水率 L∞ 差分别为 `1.59e-9`、`1.70e-13`；相对离散误差可忽略 | COMPLETED | `experiments/EXP-Q1-PICARD-SENS/` |
| EXP-Q1-NUM-REMEDIATION | Q1 | M1-NUM-T2 | 评估 BE→“BE 首步+BDF2”时间积分候选；不生成工作簿 | N=320、dt=1/0.5/0.25 s；与 BE dt=0.25 对照；完整网格及论文 7×5 | BDF2 论文点差异降至温度 `0/35`、水分 `0/35`（dt0.5→0.25）；全网格估计误差仍未通过 | COMPLETED | `experiments/EXP-Q1-NUM-REMEDIATION/` |

状态建议使用：`PLANNED` / `RUNNING` / `COMPLETED` / `FAILED` / `BLOCKED` / `ABANDONED`。

## 实验登记模板

```text
EXP-xxx
Question:
Model:
Purpose:
Key Config:
Data Version:
Code Version:
Metrics:
Status:
Evidence: experiments/EXP-xxx/
Notes:
```

正式实验至少应尽量保存：

- `config.json`
- `metrics.json`
- `notes.md`

必要时保存 `predictions.csv`、`logs.txt` 和 `artifacts/`。论文数字优先引用这里登记的结果。

## Q1 Execution Note

EXP-001 至 EXP-007 已在实现授权后按顺序运行，状态均为 `COMPLETED`。`EXP-Q1-FINAL-CONV` 先判定为 `BLOCKED`，随后在人工授权的数值整改门中完成实现审计、独立制造解基准、误差定位、Picard 敏感性和 BDF2 候选对照。BDF2 改善了论文 7×5 点的时间稳定性，但完整网格的保守估计误差仍未通过，因此 Q1 Result & Deliverable Gate 仍为 `BLOCKED`。这些是内部实现与数值验证证据，不是论文最终结论；尚未生成 `result1.xlsx`，也未写入 `deliverables/candidate/` 或 `deliverables/final/`。

每个实验目录均包含 `config.json`、`metrics.json` 和 `notes.md`，记录命令、代码提交、输入 SHA-256、求解器配置、运行时间、验证状态和产物路径。
