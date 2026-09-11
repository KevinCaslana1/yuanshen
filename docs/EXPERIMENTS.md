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

EXP-001 至 EXP-007 已在实现授权后按顺序运行，状态均为 `COMPLETED`。随后执行 `EXP-Q1-FINAL-CONV`，对完整交付网格和论文追踪点进行 Level A/Level B 检查；最细已测试配置仍未通过四位小数稳定性，因此状态为 `BLOCKED`。这些是内部实现与数值验证证据，不是论文最终结论；尚未生成 `result1.xlsx`，也未写入 `deliverables/candidate/` 或 `deliverables/final/`。

每个实验目录均包含 `config.json`、`metrics.json` 和 `notes.md`，记录命令、代码提交、输入 SHA-256、求解器配置、运行时间、验证状态和产物路径。
