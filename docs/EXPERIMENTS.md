# Experiments Index

本文件只保存正式实验的索引和关键结果；每个实验的详细配置与产物放在 `experiments/EXP-xxx/`。

## 实验索引

| ID | Question | Model | Purpose | Key Config | Metrics | Status | Evidence |
|---|---|---|---|---|---|---|---|
| EXP-001 | Q1 | M1 smoke | 检查输入、插值、单位、边界方向和最小离散 | 极小网格、短时间、附件1原始点 | 可运行性、NaN/Inf、初值、通量方向 | PLANNED | `docs/Q1_PLAN.md` |
| EXP-002 | Q1 | B0 vs M1 | 比较空间扩散模型相对均匀 Baseline 的必要性 | 同一输入、短时与设计时长两档 | 平均响应、径向差异、方向一致性 | PLANNED | `docs/Q1_PLAN.md` |
| EXP-003 | Q1 | M1 | 时间离散敏感性与收敛 | 内部时间步长候选 | 关键点差异、非线性残差 | PLANNED | `docs/Q1_PLAN.md` |
| EXP-004 | Q1 | M1 | 空间网格收敛 | `Δr=0.1,0.05,0.025 cm` 候选 | 关键点差异、剖面平滑性 | PLANNED | `docs/Q1_PLAN.md` |
| EXP-005 | Q1 | M1 vs M3 | Robin 与 Dirichlet 边界敏感性 | 相同输入和网格 | 表面滞后、中心响应、通量 | PLANNED | `docs/Q1_PLAN.md` |
| EXP-006 | Q1 | M1 | 分段线性与零阶保持输入敏感性 | 不修改附件1原始点 | 关键输出差异、边界曲线 | PLANNED | `docs/Q1_PLAN.md` |
| EXP-007 | Q1 | M1 | 通量、储量和物理范围 sanity check | 完整设计时长、收敛配置 | 守恒残差、范围、异常日志 | PLANNED | `docs/Q1_PLAN.md` |

状态建议使用：`PLANNED` / `RUNNING` / `COMPLETED` / `FAILED` / `ABANDONED`。

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

## Q1 Planning Note

EXP-001 至 EXP-007 当前全部为 `PLANNED`，尚未运行，均不是论文证据。本轮只完成设计登记，不创建 `experiments/EXP-xxx/` 正式产物，不生成 `result1.xlsx`。
