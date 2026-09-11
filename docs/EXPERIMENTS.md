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
| EXP-Q1-INITIAL-LAYER | Q1 | M1/BE diagnostic | 检查 t=0 温度/水分 Robin 相容性、扩散尺度和 0–10 s 早期层 | N=320/640/1280；dt=.25/.125/.0625/.03125 s；t=.25/.5/1/2/5/10 s；R、R-dr、R-2dr、1.9 cm | 水分初始 Robin 残差 `-2.024296e-6 m/s`；t=1 s 均匀 N1280 表面保守不确定度 `8.7151e-5 kg/kg` | COMPLETED | `experiments/EXP-Q1-INITIAL-LAYER/` |
| EXP-Q1-BDF2-STARTUP | Q1 | M1-NUM-T2 | 对照标准 BE 首步与 0–1 s 早期 BE 子步启动 | N=640、正常 dt=.25 s；启动 dt=.25/.125/.0625 s；t=.25/.5/1/2/5/10 s | 早期子步未相对标准启动稳定改善；最大标准/早期差异 `1.5769e-3 kg/kg` | COMPLETED | `experiments/EXP-Q1-BDF2-STARTUP/` |
| EXP-Q1-SURFACE-DECAY | Q1 | M1/BE | 测量 1–100 s 表面空间误差衰减并绘图 | N320/N640/N1280，共同 dt=.0625 s；r=1.9/2.0 cm | r=2.0 cm N640→N1280 误差从 t=1 的 `3.0796e-4` 降到 t=100 的 `2.1780e-5 kg/kg`，比值约 `14.14` | COMPLETED | `experiments/EXP-Q1-SURFACE-DECAY/` |
| EXP-Q1-CLUSTER-BENCH | Q1 | Isolated nonuniform FVM benchmark | 验证边界聚类保守 FVM 的中心/内部/表面空间与时间阶 | 制造解；聚类幂 `p=2`；多级空间/时间细化 | 空间 L∞ 阶约 `1.95–1.96`，时间 L∞ 阶约 `1.01–1.06`；中心/表面趋势正常 | COMPLETED | `experiments/EXP-Q1-CLUSTER-BENCH/` |
| EXP-Q1-CLUSTER-SHORT | Q1 | M1/BE nonuniform candidate | 在真实 Q1 上比较均匀与边界聚类网格的 0–10 s 空间误差 | 均匀 N320/N640；聚类 base320/base640/base1280；dt=.0625 s；显式保留官方输出节点 | t=1 s 聚类 base640→base1280 表面差 `3.6753e-6`，远低于均匀 N320→N640 的 `1.3891e-3` | COMPLETED | `experiments/EXP-Q1-CLUSTER-SHORT/` |
| EXP-Q1-CLUSTER-TEMPORAL | Q1 | M1/BE nonuniform candidate | 对聚类候选执行固定网格时间梯、t=1 全 21 点空间/时间误差与舍入认证 | base640 dt=.25/.125/.0625/.03125；base1280 dt=.0625/.03125/.015625/.0078125；base320/base640/base1280 dt=.03125 | `C(R,1s)=2.5177587784`；时间剩余 `3.1850e-5`、空间剩余 `1.2259e-6 kg/kg`；20/21 certified，表面 ambiguous | COMPLETED | `experiments/EXP-Q1-CLUSTER-TEMPORAL/` |
| EXP-Q1-FULL-SPATIAL | Q1 | M1-NUM-T2 clustered FVM | 全时域空间收敛与逐点离散不确定度 | cluster base320/base640/base1280，固定 BDF2 `dt=0.125 s`；`1800×21` 与论文 `7×5` | 空间细层最大估计不确定度：温度 `3.5588e-7 °C`、含水率 `1.2258e-6 kg/kg`；3 层空间阶和 Richardson 已记录 | COMPLETED | `experiments/EXP-Q1-FULL-SPATIAL/` |
| EXP-Q1-FULL-TEMPORAL | Q1 | M1-NUM-T2 clustered FVM | 全时域时间收敛与逐点离散不确定度 | cluster base1280，BDF2 `dt=0.25/0.125/0.0625 s`；`1800×21` 与论文 `7×5` | 时间细层最大估计不确定度：温度 `4.2626e-7 °C`、含水率 `5.5889e-6 kg/kg`；局部 Richardson 不稳定点保留原始细层差值包络 | COMPLETED | `experiments/EXP-Q1-FULL-TEMPORAL/` |
| Q1_FREEZE_RUN | Q1 | Frozen M1-NUM-T2 production | 从零双跑冻结生产配置、内部全场保存、确定性与候选溯源 | cluster base320（实际 `338` intervals），BDF2 `dt=0.25 s`，`0..1800 s` | 两次完整内部场 SHA-256 相同；运行验证均 PASS；candidate 与论文 35/35 点 trace PASS | COMPLETED | `experiments/Q1_FREEZE_RUN/` |
| Q1_FINAL_FREEZE | Q1 | Frozen M1-NUM-T2 production | 人工批准后的 candidate-to-final 隔离复制、最终工作簿结构/数值/格式和哈希校验 | `deliverables/candidate/result1.xlsx` → `deliverables/final/result1.xlsx`；无 solver 重跑 | candidate/final SHA-256 相同；final validator PASS；官方模板哈希与 `A题/` 完整性 PASS | COMPLETED | `experiments/Q1_FINAL_FREEZE/`、`deliverables/final/Q1_MANIFEST.json` |
| Q1-FIGURES | Q1 | Frozen M1-NUM-T2 production | 从冻结内部输出生成论文候选图表及验证数据，不改变数值结果 | 9 figures；PNG/SVG；核心图表与空间/时间验证图 | 图表源哈希受保护；纸面点 70/70；随机图表数据点 20/20；视觉 QA PASS | COMPLETED | `figures/q1/`、`docs/Q1_VISUALIZATION.md` |

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

EXP-001 至 EXP-007 已在实现授权后按序完成。后续完成初始层诊断、BDF2 启动对照、表面误差衰减、聚类 benchmark、真实 Q1 短时聚类对照、聚类时间梯及全时域空间/时间收敛。`D-Q1-NUM-ACCURACY-CRITERION` 下，3 层空间与 3 层时间的逐点估计不确定度均通过 `<5e-5`；随后 `Q1_FREEZE_RUN` 双跑确定性通过，并从 run_1 生成候选。人工 freeze approval 已批准并完成 candidate-to-final 复制、最终验证和图表生成；Q1 现已冻结，Q2 不启动。历史实验中的 BLOCKED 记录保留为历史证据，不代表当前冻结配置失败。

每个实验目录均包含 `config.json`、`metrics.json` 和 `notes.md`，记录命令、代码提交、输入 SHA-256、求解器配置、运行时间、验证状态和产物路径。
