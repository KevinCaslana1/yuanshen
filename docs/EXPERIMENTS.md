# Experiments Index

本文件只保存正式实验的索引和关键结果；每个实验的详细配置与产物放在 `experiments/EXP-xxx/`。

## 实验索引

| ID | Question | Model | Purpose | Key Config | Metrics | Status | Evidence |
|---|---|---|---|---|---|---|---|
| EXP-001 | Q1 | M1 smoke | 检查输入、插值、单位、边界方向和最小离散 | 10 s、N=8、附件1原始点 | 所有运行检查通过，Picard max=2 | COMPLETED | `experiments/EXP-001/` |
| EXP-002 | Q1 | B0 vs M1 vs M2 | 比较均匀 Baseline、非线性径向和常-D径向模型 | 1800 s、dt=1 s、N=80 | M1/M2验证通过；平均响应与径向差异已记录 | COMPLETED | `experiments/EXP-002/` |
| EXP-003 | Q1 | M1/BE | 固定空间网格的完整时间收敛审计 | 固定 `dr=0.025 cm`；`dt=1/0.5/0.25/0.125 s`；`dt=0.0625 s` reference；0–1800 s | 相邻直接差分 observed order：表面 L∞ `0.929/0.962`，内部约 `0.999–1.010`；各位置 L∞/L2 均随 dt 下降 | COMPLETED | `experiments/EXP-003/` |
| EXP-004 | Q1 | M1/BE | 固定时间步的完整空间收敛审计 | 固定 `dt=0.0625 s`；`dr=0.1/0.05/0.025 cm`；`dr=0.0125 cm` reference；0–1800 s | 相邻直接差分 observed order：表面 L∞ `0.941`、L2 `1.747`；r=1.5/1.0 cm L∞ `1.933/1.978` | COMPLETED | `experiments/EXP-004/` |
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
| EXP-Q1-SURFACE-DECAY | Q1 | M1/BE | signed/absolute 表面误差、早期深谷与边界求解过程审计 | N640/N1280，共同 `dt=.0625 s`；1–100 s；r=1.9/2.0 cm；0–60 s solver trace | r=1.9 cm 在 35–36 s signed error 穿零，估计 `35.2521507920 s`；r=2.0 cm 无穿零；归类 cancellation dip | COMPLETED | `experiments/EXP-Q1-SURFACE-DECAY/` |
| EXP-Q1-CLUSTER-BENCH | Q1 | Isolated nonuniform FVM benchmark | 验证边界聚类保守 FVM 的中心/内部/表面空间与时间阶 | 制造解；聚类幂 `p=2`；多级空间/时间细化 | 空间 L∞ 阶约 `1.95–1.96`，时间 L∞ 阶约 `1.01–1.06`；中心/表面趋势正常 | COMPLETED | `experiments/EXP-Q1-CLUSTER-BENCH/` |
| EXP-Q1-CLUSTER-SHORT | Q1 | M1/BE nonuniform candidate | 在真实 Q1 上比较均匀与边界聚类网格的 0–10 s 空间误差 | 均匀 N320/N640；聚类 base320/base640/base1280；dt=.0625 s；显式保留官方输出节点 | t=1 s 聚类 base640→base1280 表面差 `3.6753e-6`，远低于均匀 N320→N640 的 `1.3891e-3` | COMPLETED | `experiments/EXP-Q1-CLUSTER-SHORT/` |
| EXP-Q1-CLUSTER-TEMPORAL | Q1 | M1/BE nonuniform candidate | 对聚类候选执行固定网格时间梯、t=1 全 21 点空间/时间误差与舍入认证 | base640 dt=.25/.125/.0625/.03125；base1280 dt=.0625/.03125/.015625/.0078125；base320/base640/base1280 dt=.03125 | `C(R,1s)=2.5177587784`；时间剩余 `3.1850e-5`、空间剩余 `1.2259e-6 kg/kg`；20/21 certified，表面 ambiguous | COMPLETED | `experiments/EXP-Q1-CLUSTER-TEMPORAL/` |
| EXP-Q1-FULL-SPATIAL | Q1 | M1-NUM-T2 clustered FVM | 全时域空间收敛与逐点离散不确定度 | cluster base320/base640/base1280，固定 BDF2 `dt=0.125 s`；`1800×21` 与论文 `7×5` | 空间细层最大估计不确定度：温度 `3.5588e-7 °C`、含水率 `1.2258e-6 kg/kg`；3 层空间阶和 Richardson 已记录 | COMPLETED | `experiments/EXP-Q1-FULL-SPATIAL/` |
| EXP-Q1-FULL-TEMPORAL | Q1 | M1-NUM-T2 clustered FVM | 全时域时间收敛与逐点离散不确定度 | cluster base1280，BDF2 `dt=0.25/0.125/0.0625 s`；`1800×21` 与论文 `7×5` | 时间细层最大估计不确定度：温度 `4.2626e-7 °C`、含水率 `5.5889e-6 kg/kg`；局部 Richardson 不稳定点保留原始细层差值包络 | COMPLETED | `experiments/EXP-Q1-FULL-TEMPORAL/` |
| Q1_FREEZE_RUN | Q1 | Frozen M1-NUM-T2 production | 从零双跑冻结生产配置、内部全场保存、确定性与候选溯源 | cluster base320（实际 `338` intervals），BDF2 `dt=0.25 s`，`0..1800 s` | 两次完整内部场 SHA-256 相同；运行验证均 PASS；candidate 与论文 35/35 点 trace PASS | COMPLETED | `experiments/Q1_FREEZE_RUN/` |
| Q1_FINAL_FREEZE | Q1 | Frozen M1-NUM-T2 production | 人工批准后的 candidate-to-final 隔离复制、最终工作簿结构/数值/格式和哈希校验 | `deliverables/candidate/result1.xlsx` → `deliverables/final/result1.xlsx`；无 solver 重跑 | candidate/final SHA-256 相同；final validator PASS；官方模板哈希与 `A题/` 完整性 PASS | COMPLETED | `experiments/Q1_FINAL_FREEZE/`、`deliverables/final/Q1_MANIFEST.json` |
| Q1-FIGURES | Q1 | Frozen M1-NUM-T2 production | 从冻结内部输出生成论文候选图表及验证数据，不改变数值结果 | 9 figures；PNG/SVG；核心图表与空间/时间验证图 | 图表源哈希受保护；纸面点 70/70；随机图表数据点 20/20；视觉 QA PASS | COMPLETED | `figures/q1/`、`docs/Q1_VISUALIZATION.md` |
| EXP-Q2-PROPERTY-POINTS | Q2 | Q2_PROPERTY_SPEC | 审计附录3公式、单位、Kelvin 处理、正域和单调性探针 | 公式点 `C=0.15..2.55`、`T=301.15..323.15 K`；域保护 | 所有设计检查 true；不运行 solver、不写工作簿 | COMPLETED | `experiments/EXP-Q2-PROPERTY-POINTS/` |
| EXP-Q2-ENV-TAIL | Q2 | Environment tail audit | 审计附件1最后10/20/40/80点，供 `14400 s` 后环境决策 | 只读 `Sheet1`；241点；60 s 间隔 | 尾段均值/标准差/最后点/趋势已保存；不选择环境延续 | COMPLETED | `experiments/EXP-Q2-ENV-TAIL/` |
| EXP-Q2-ENV-INTERPOLATION | Q2 | Environment candidates | 比较分段线性与 PCHIP 的输入和 0–3 h 输出敏感性 | 原始点保持不变；A/B 候选 | 尚未实现/运行 | PLANNED | `docs/Q2_PLAN.md` |
| EXP-Q2-COUPLED-PICARD | Q2 | Q2-M1 | 验证双场 block Gauss–Seidel/Picard 的收敛、松弛和失败关闭 | 分场归一化残差；候选 tol `1e-8`、max50 | 尚未实现/运行 | PLANNED | `docs/Q2_PLAN.md` |
| EXP-Q2-VARCOEF-FVM | Q2 | Q2-M1 | 比较变 `k,D` 界面算术/调和平均的守恒与一致性 | 常系数、光滑变系数、强梯度 benchmark | 尚未实现/运行 | PLANNED | `docs/Q2_PLAN.md` |
| EXP-Q2-Q1-OVERLAP | Q2 | Q2-M1 vs Q1 frozen | 在 `0..1800 s` 仅做量级/中心/表面/界面交叉检查 | 相同几何/输入窗口；物性差异显式保留 | 尚未实现/运行；不预期数值相等 | PLANNED | `docs/Q2_PLAN.md` |
| EXP-Q2-RESTART | Q2 | Q2-M1 | 验证连续运行与 checkpoint restart 等价 | 保存场、历史层、config、环境状态、hash、commit SHA | 尚未实现/运行 | PLANNED | `docs/Q2_PLAN.md` |

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

## Q2 V3 PRODUCTION FREEZE RUN

| ID | Question | Model | Purpose | Key Config | Metrics | Status | Evidence |
|---|---|---|---|---|---|---|---|
| Q2_FREEZE_RUN_V3 | Q2 | Frozen Q2-M1 candidate A | 人工批准后的独立 Run1/Run2 生产、被动 horizon、determinism、official candidate 与图表 lineage | n=320/cluster3；harmonic；early `dt=.015625 s` through 5 s；production `dt=.25 s`；BE startup/BDF2；14400 s BE restart；ENV-B；official t=1..228536 s×21 radii | Run1/Run2 raw/sampled/diagnostics byte/hash identical；Picard non-converged=0；candidate trace 100/100、Table3/4 60/60；figure trace 30/30 | COMPLETED；V3 production source and candidate gates PASS | `experiments/Q2_FREEZE_RUN_V3/`、`deliverables/candidate/result2.xlsx`、`figures/q2/` |

V3 的唯一 production source 是 Run1；Run2 仅为 `DETERMINISM_REFERENCE`。旧 `Q2_FREEZE_RUN`、V2 aborted attempt、V3 错误 horizon attempt 和 V3 postprocessing failure 均仅保留 provenance，不得进入 workbook 或正式图表来源。

## Q2 V3 Final Freeze（2026-09-12）

人工批准 `Q2 V3 production freeze = APPROVED` 后，未重新计算 Q2 或重新生成图表，仅将已验证 candidate `result2.xlsx` 和 11 组 PNG/SVG 按字节原样复制到 final。candidate/final 工作簿 SHA-256 与大小一致；两张表均为 `228537×22`，无公式，数据区 `0.0000` 格式，workbook trace `100/100`、Table3/4 `60/60`。final 图表为 11 组/22 个文件，PNG ≥300 dpi，trace `30/30`。完整测试结果为 `56 passed`。

证据：`experiments/Q2_FINAL_FREEZE/freeze_record.json`、`deliverables/final/Q2_MANIFEST.json`。历史失败实验 `Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912` 保持原样并继续标记为 `NOT_DELIVERY_SOURCE`。

## Q1 Surface Signed-Error Audit Addendum

本轮按用户要求暂停 Q2/Q3/Q4，并对早期表面误差单独复核。历史表面比较脚本曾只把 `abs(C_test-C_ref)` 写入指标；本次审计保留完整浮点的 `signed_error=e=C_test-C_ref` 与 `absolute_error=abs(e)`，并同时生成未取绝对值图和 absolute-error semilogy 图。N640 与 N1280 使用共同 `dt=0.0625 s`，1–100 s 逐秒输出；15–45 s 原始表和 0–60 s 边界/求解轨迹均在 `experiments/EXP-Q1-SURFACE-DECAY/`。

在 r=1.9 cm 处，35 s 的 signed error 为 `-7.767662335567138e-08`，36 s 为 `+2.303796104996536e-07`，线性穿零估计为 `35.252150792027635 s`；r=2.0 cm 字面表面在 15–45 s 没有穿零。固定 `dt=0.0625 s` 的空间对照中，r=1.9 cm 谷值/穿零随 `dr=0.1/0.05/0.025 cm` 移动至约 `43.817/40.089/37.124 s`，而全局 L∞/L2 仍随细化下降。该现象应记录为 `pointwise error zero-crossing / cancellation dip`，不能作为算法精度突然提高两个数量级的证据。

独立过程检查确认 0–60 s 的 `C_inf` 使用同一线性段（原始端点 `0.01963`、`0.02002 kg/kg`，斜率 `6.4999999999999666e-06 kg/kg/s`，整数采样最大二阶差 `3.469446951953614e-18`）；`dt=0.0625 s` 固定，960 个步的 Picard 次数均为 2，最终归一化非线性残差最大 `9.959320862560113e-09`，归一化 time-step residual 最大 `5.662603714766902e-16`，时间/索引对齐误差为 0。15–45 s 的 literal one-sided Robin 通量差最大 `5.341027496999451e-07`，face 通量差最大 `5.267304447720662e-07`，但表面控制体积方程残差最大 `3.4778292694089816e-17`；未发现与深谷同步的边界或迭代突变。

EXP-003/004 是与冻结生产配置隔离的 uniform-grid BE 诊断：时间审计固定 `dr=0.025 cm`，空间审计固定 `dt=0.0625 s`，两者都保留固定 reference 的全时域 L∞/L2 以及相邻方案的 observed order。Q1 final workbook、`figures/q1/final/` 和 `A题/` 在本轮均未修改。

## Q2 Design Gate Execution Note

`EXP-Q2-PROPERTY-POINTS` 和 `EXP-Q2-ENV-TAIL` 是设计阶段的只读审计，已分别由 `scripts/audit_q2_property_spec.py` 和 `scripts/audit_q2_environment_tail.py` 复现；两者均明确 `formal_Q2_solver_run=false`、`workbook_written=false`。其余 Q2 实验保持 `PLANNED`，必须等待人工 implementation authorization，且先解决或显式承认 `OQ-Q2-ENV-001/002`、`OQ-Q2-END-001`、`OQ-Q2-FVM-001` 和 `OQ-Q2-ACC-001`。

## Q2 Implementation & Short-Horizon Validation Addendum

收到人工授权后，Q2 实施和短时验证已完成。以下实验均只写入 `experiments/EXP-Q2-xxx/` 的 CSV/JSON/PNG/诊断文件；没有生成、复制或修改 `result2.xlsx`，没有启动 Q3/Q4。

| ID | Purpose | Key Config | Key Result | Status | Evidence |
|---|---|---|---|---|---|
| EXP-Q2-001 | 0–60 s smoke | Candidate A；clustered FVM；BDF2 after BE startup；`dt=.25 s`；80 requested intervals | 240 steps；Picard `min/median/p95/max=3/3/3/3`；有限值、范围、边界/线性残差检查通过 | COMPLETED | `experiments/EXP-Q2-001/` |
| EXP-Q2-002 | Q1/Q2 0–1800 s overlap sanity | Q1 frozen run vs Q2 A；相同附件1窗口；`dt=.25 s` | 量级、连续性、中心/表面和求解稳定性检查通过；Q1/Q2 数值不要求相等 | COMPLETED | `experiments/EXP-Q2-002/` |
| EXP-Q2-003 | 独立变系数 FVM benchmark | 制造解；变量径向 heat/moisture coefficient；BE；空间/时间细化 | 空间约一阶、BE 时间约一阶；结果与当前 Robin 节点闭合一致 | COMPLETED | `experiments/EXP-Q2-003/` |
| EXP-Q2-004 | Coupled Picard convergence | 0–300 s；Candidate A；`dt=.25 s`；80 intervals | 1200 步全部收敛；Picard `3/3/3/3`；双场残差与线性残差记录完整 | COMPLETED | `experiments/EXP-Q2-004/` |
| EXP-Q2-005 | Time sensitivity | 固定 uniform `dr=.025 cm`；BE；`dt=1,.5,.25,.125 s`；`dt=.03125 s` reference | 温度 observed order `1.047/1.099/1.222/1.585`；水分 `0.999/1.072/1.206/1.577` | COMPLETED | `experiments/EXP-Q2-005/` |
| EXP-Q2-006 | Space sensitivity | 固定 `dt=.125 s`；uniform `dr=.1,.05,.025 cm`；`.0125 cm` reference | 温度 L∞、L2 与水分 L∞、L2 均随细化下降；同一物理半径比较 | COMPLETED | `experiments/EXP-Q2-006/` |
| EXP-Q2-007 | BE/BDF2 comparison | Candidate A/B；`dt=.25 s`；0–600 s；共同细参考 | A 上 BDF2 的温度/水分 accuracy proxy 均低于 BE；状态仅记为 `RECOMMENDED_FOR_Q2_FREEZE` | COMPLETED | `experiments/EXP-Q2-007/` |
| EXP-Q2-008 | Environment interpolation | linear executable；PCHIP optional | linear 保持原始点；SciPy 不可用，PCHIP 未伪造，`OQ-Q2-ENV-002` 保持 OPEN | PARTIAL_OPEN | `experiments/EXP-Q2-008/` |
| EXP-Q2-009 | Mass/heat/Robin residual | 0–300 s；Candidate A；BDF2 | 逐步质量、热量、Robin 通量差和线性残差均有完整日志 | COMPLETED | `experiments/EXP-Q2-009/` |
| EXP-Q2-010 | Checkpoint/restart | 0–600 s；300 s checkpoint；Candidate A；BDF2 | 连续/重启末场最大差值为 0；checkpoint 含输入哈希、commit、网格、配置和历史层 | COMPLETED | `experiments/EXP-Q2-010/` |
| EXP-Q2-011 | Internal 0–3 h validation | Candidate A；160 intervals；BDF2；`dt=.25 s`；0–10800 s | 43200 步完成；Picard `2/2/3/3`；性质范围和纸面时刻 1800–10800 s 已记录 | COMPLETED | `experiments/EXP-Q2-011/` |

正式设计表中的 `EXP-Q2-ENV-INTERPOLATION`、`EXP-Q2-COUPLED-PICARD`、`EXP-Q2-VARCOEF-FVM`、`EXP-Q2-Q1-OVERLAP`、`EXP-Q2-RESTART` 是设计阶段名称；本附录的 `EXP-Q2-008/004/003/002/010` 为实施阶段实际证据编号。开放问题不因实验完成而静默关闭。

## Q2 Long-Horizon Boundary & Production Config Gate Addendum（2026-09-11）

本阶段依据人工授权执行边界尾段、插值、边界参数、界面平均、0–72 h稳定性、低含水率物性、守恒/Robin、checkpoint/restart、长时收敛和 Baseline 复核。所有运行均不写入 `result2.xlsx`，不停止 Q3 事件，不启动 Q3/Q4。`A题/`、Q1 solver、Q1 final workbook 和 Q1 figures 未修改。

| ID | Purpose | Key Config / Scope | Key Result | Status | Evidence |
|---|---|---|---|---|---|
| EXP-Q2-012 | Environment tail and transition audit | Attachment 1 raw 241 points；10/20/40/60/80-point tail；0–14400 s；representative surface | last raw=`50.165 °C/0.04986 kg/kg`；tail40 mean=`49.99525 °C/0.049988 kg/kg`；ENV-A last-raw continuation has no post-14400 jump，ENV-B/team-reference would introduce a measurable input jump | PASS as audit；OQ-ENV-001 OPEN | `experiments/EXP-Q2-012-ENVIRONMENT/` |
| EXP-Q2-013 | Linear versus PCHIP | same raw knots；Candidate A；`n=80`；`dt=1 s`；0–14400 s | both methods reproduce every raw knot exactly；0–4 h max difference `0.0089368847 °C` / `1.6431732e-5 kg/kg`，not negligible for silent substitution | PASS as comparison；human review required，OQ-ENV-002 OPEN | `experiments/EXP-Q2-013-INTERPOLATION/` |
| EXP-Q2-014 | h/hm carryover sensitivity | Candidate A；`n=80`；`dt=1 s`；0–21600 s；each of h/hm ±10% separately | h sensitivity low (`max ΔT≈0.05079/0.03408 °C`，`max ΔC≈0.004545/0.003620`)；hm sensitivity medium (`max ΔT≈0.00592/0.00527 °C`，`max ΔC≈0.07966/0.07099`)；all runs converged | PASS as sensitivity；OQ-BC-001 OPEN | `experiments/EXP-Q2-014-BC-SENSITIVITY/` |
| EXP-Q2-015 | Arithmetic versus harmonic face mean | real Q2 0–10800 s；`n=80`；`dt=.25 s`；plus manufactured benchmark | short real-run max difference `1.36852384e-6 K` / `4.94771902e-7 kg/kg`；benchmark preserves expected conservation/order；arithmetic remains provisional only pending long-horizon check | PASS as comparison；OQ-FVM-001 OPEN | `experiments/EXP-Q2-015-INTERFACE-MEAN/` |
| EXP-Q2-016-A | Long ENV-A production candidate | Candidate A；`n=80`；`dt=.25 s`；BDF2；linear；harmonic；post constant=`50.165 °C/0.04986 kg/kg`；0–259200 s；6/12/24/48/72 h stages | all stages finite and positive；final stage Picard `2/2/2/2`；`C=0.0516273..2.55 kg/kg`；`D_min=2.6499e-12 m²/s`；mass residual `2.34e-11`；heat residual `1.78e-10 J`；passive threshold bracket `205913–205913.25 s` and never used as stop | PASS with recovered output artifact；candidate not frozen | `experiments/EXP-Q2-016-LONG-ENV-A-last-raw/` |
| EXP-Q2-016-B | Long ENV-B comparator | same as A；post constant=tail40 mean `49.99525 °C/0.049988 kg/kg`；0–72 h | completed all stages；kept separate because post-14400 choice materially changes the field | PASS as comparator；OQ-ENV-001 OPEN | `experiments/EXP-Q2-016-LONG-ENV-B-tail40-mean/` |
| EXP-Q2-017 | Long time/space convergence | 0–259200 s；A reference `n=80, dt=.25 s` recovered output；time `dt=1,.5`；space `n=20,40`；checkpoints 6/12/24/48/72 h | no long-time error growth or non-finite field；versus finest reference proxies: time temp/moisture `2.987/2.307`，space temp/moisture `0.881/2.425`；these are not authoritative orders and formal short-horizon orders remain in EXP-Q2-005/006 | PASS as long stability evidence | `experiments/EXP-Q2-017-LONG-CONVERGENCE/` |
| EXP-Q2-018 | ENV-A versus ENV-B checkpoint comparison | same `n=80, dt=.25 s`；6/24/48/72 h | max A/B difference at 6/24/48/72 h: temperature `0.169486/0.169750/0.169750/0.169750 °C`；moisture `0.0014492/0.0007154/0.0003763/0.0002776 kg/kg` | PASS as decision evidence；does not close environment OQ | `experiments/EXP-Q2-018-ENV-COMPARISON/` |
| EXP-Q2-019 | Long checkpoint/restart | continuous 0–24 h versus restart from 12 h checkpoint to 24 h；A；`n=80`；`dt=.25 s` | final temperature and moisture field differences both exactly `0.0` at machine comparison tolerance | PASS | `experiments/EXP-Q2-019-LONG-RESTART/` |
| EXP-Q2-020 | Q2-B0 finite-cost control | A coupled versus fixed Appendix-3 properties at initial state；0–21600 s；`n=80`；`dt=.5 s` | B0 runtime `13.70 s` vs coupled `65.99 s`；cost ratio `0.2077`；at 6 h ΔT `0.000439 °C`，ΔC `0.392241 kg/kg`；B0 is control, not substitute | PASS as baseline | `experiments/EXP-Q2-020-BASELINE/` |

### Long-horizon artifact note

The first ENV-A append-only output was interrupted after a stage resume had already advanced the files past the old checkpoint cursor. The raw files are retained unchanged as evidence and are explicitly marked invalid as a one-second grid (`97,104` duplicated sample rows and `4,624` duplicated diagnostic rows). `official_samples_recovered.csv` and `diagnostics_1s_recovered.csv` retain the first row per deterministic `(time_s,radius_cm)` or `time_s` key, contain the expected `5,443,221` sample rows and `259,200` diagnostic rows, and are the only files used by long plots and convergence comparisons. The solver now truncates append-only outputs to the checkpoint cursor before restart to prevent recurrence.

### Gate interpretation

The numerical candidate is suitable for human review, but no open modeling choice is silently closed. Provisional recommendation is ENV-A last raw point after 14400 s, linear interpolation, harmonic face mean, and Q1-carried h/hm with the sensitivity evidence attached; the long-horizon arithmetic comparison is retained in EXP-Q2-021 and does not support a silent arithmetic freeze. The recommendation remains `PENDING_HUMAN_APPROVAL`. Q2 internal validation may use 72 h as a stability horizon, but Q2 official endpoint/row count remains open. The observed `C<0.15` bracket is passive evidence only and does not authorize Q3 or define the Q2 deliverable endpoint.

## Q2 Human Model-Decision Freeze Packet Addendum（2026-09-11）

本阶段建立 `docs/Q2_HUMAN_DECISION_PACKET.md`，不生成 workbook。既有实验中的缺失决策数据仅补做了一个小规模 targeted 实验 `EXP-Q2-021-DECISION-TARGETS`：

| ID | Scope | Configuration | Key result | Status | Evidence |
|---|---|---|---|---|---|
| EXP-Q2-021-DECISION-TARGETS-BC-LONG | h/hm 3 h、6 h、24 h、48 h、72 h 检查点和 passive bracket | Candidate A；n=80；BDF2；linear；harmonic；`dt=2 s`；只写紧凑 diagnostics | h±10% 的72 h moisture L∞ `4.91–6.03e-6`；hm±10% 为 `3.94–5.10e-4`；hm bracket shift `-2076/+2646 s` | PASS；targeted screen，不是 production accuracy | `experiments/EXP-Q2-021-DECISION-TARGETS/boundary_long_target_metrics.json` |
| EXP-Q2-021-DECISION-TARGETS-INTERFACE-LONG | arithmetic/harmonic 长时代表点 | arithmetic；ENV-A；n=80；BDF2；linear；`dt=.25 s`；同 canonical checkpoint | 6/24/48/72 h moisture L∞ `1.52e-6/1.40e-4/1.27e-4/1.01e-4`；temperature L∞ `2.00e-9` 以下 | PASS；decision evidence | `experiments/EXP-Q2-021-DECISION-TARGETS/interface_long_target_metrics.json` |
| Q2_FREEZE_RUN | Q2 | Approved Candidate A production double run | ENV-B；实际98 cells；`dt=.25 s`；BDF2；linear；harmonic；`0..228635 s` | 双跑 hash identical；accuracy gate FAIL；candidate blocked | BLOCKED | `experiments/Q2_FREEZE_RUN/` |
| Q2-ACCURACY-CONFIRMATION | Q2 | Independent full-region temporal/spatial confirmation | same input/code；`dt=.125/.5 s`；`n=160`；fresh `t=0` | T/C L∞=`1.9082e-4/2.0357e-4`；T/C L2=`4.4001e-6/3.0182e-5`；order=`1.6685/3.0631` | FAILED | `experiments/Q2_FREEZE_RUN/accuracy_confirmation.json` |

第一次 interface target 的后处理曾请求 canonical 未保存的 `10800 s` 键而退出；solver 已完整运行但该次结果未被采纳，修复后只用 canonical 已存在的 6/24/48/72 h 键重跑并通过。详情写入 `docs/FAILURES.md`。

本轮推荐状态统一为 `RECOMMENDED_FOR_HUMAN_APPROVAL`；D4 根据长时 moisture 差异撤回“arithmetic 可直接冻结”的 provisional 解释，当前推荐保留 harmonic，仍等待人工决定。

## Q2 Production Freeze Run and Accuracy Confirmation（2026-09-12）

最新人工授权批准 Q2 production freeze 后，执行了独立 fresh-from-`t=0` Run1/Run2 及精度确认。Run1 仅作为失败尝试 provenance；Run2 只作确定性参考，当前没有 formal production source。配置为 Candidate A、实际 98-cell boundary-clustered conservative FVM、`dt=.25 s`、BE startup/BDF2、linear、harmonic、ENV-B post-14400 constants、`final_horizon=228635 s`。两次生产 raw/sampled/diagnostics/checkpoint 均 byte/hash identical，生产场和迭代/属性/守恒/Robin/中心对称检查通过。

| Experiment | Purpose | Key result | Status | Evidence |
|---|---|---|---|---|
| Q2_FREEZE_RUN | Approved production freeze double run | Run1/Run2 complete and deterministic；failed provenance only；passive observer bracket `[207034.5,207034.75] s`；no workbook | BLOCKED at accuracy gate | `experiments/Q2_FREEZE_RUN/` |
| Q2-ACCURACY-CONFIRMATION | Same-input temporal/spatial reference confirmation | Against dt=.125/n=160: T L∞ `1.9082196854469657e-4 °C`、C L∞ `2.0357404664261836e-4 kg/kg`；T/C L2 `4.400124076121024e-6`/`3.0182278875418313e-5`；observed order T/C `1.6685/3.0631` | FAILED | `experiments/Q2_FREEZE_RUN/accuracy_confirmation.json` |

诊断显示 temporal 温度峰位于 `t=14401 s,r=2.0 cm`，与冻结环境在 `14400 s` 后的 `-0.16975 °C` 跳变一致；spatial 水分峰位于 `t=1 s,r=2.0 cm`，属于初始表面层分辨率敏感点。该结果证明当前候选未达到内部精度门，不证明存在随机性或绘图 artifact；未生成 candidate workbook、Q2 figures、Table 3/4 traceability 或 final result2。

## Q2 Numerical Accuracy Remediation Addendum（2026-09-12）

本阶段依据人工授权执行 Q2 数值精度整改；不改变 ENV-B、`h/hm`、官方初值、harmonic interface、物性公式或 horizon 规则，不生成 `result2.xlsx`，不生成 Q2 正式图，不启动 Q3/Q4。

| Experiment | Purpose | Key result | Status | Evidence |
|---|---|---|---|---|
| EXP-Q2-ACC-C-INITIAL | 独立复算 Q2 初始表面 Robin 相容性 | `C0=2.55`、`C_inf(0)=.01963`、`D=5.641680373025664e-9`；初始 Robin residual `-2.0242959999999997e-6 kg/(m²·s)` | COMPLETED；仅数值初始层发现 | `experiments/EXP-Q2-ACC-C-INITIAL/` |
| EXP-Q2-ACC-T-TRANSITION | 当前跨跳变 BDF2 与 event-aligned BE restart 局部细化 | event-aligned common-time fine/coarse raw bound T/C `8.1432e-7/1.5011e-10`；当前方案约 `4.2052e-5/1.0276e-8` | PASS as local remedy evidence；不等于 full-horizon PASS | `experiments/EXP-Q2-ACC-T-TRANSITION/` |
| EXP-Q2-ACC-SPATIAL / TEMPORAL | 分离空间和时间误差 | n320→n640 fixed-dt C L∞ `1.29798e-5`；n640 dt=.015625→.0078125 C L∞ `2.65296e-6` | COMPLETED；raw bounds，不称 Richardson | `experiments/EXP-Q2-ACC-SPATIAL*/`, `EXP-Q2-ACC-TEMPORAL*/` |
| EXP-Q2-ACC-SPATIAL-CLUSTER3 | n320 stronger surface clustering candidate | 对 n640/cluster2，T/C L∞ `1.0052e-8/2.5626e-6` through 2 s | SHORT CANDIDATE STUDY | `experiments/EXP-Q2-ACC-SPATIAL-CLUSTER3/` |
| EXP-Q2-NUM-REMEDY-C-TIME | 早期时间细化政策 | t≤2 s 与 uniform dt=.015625 逐点一致；残差有限 | COMPLETED；未单独批准生产 | `experiments/EXP-Q2-NUM-REMEDY-C-TIME/` |
| EXP-Q2-V2-REGRESSION | n320/cluster3 candidate 0–3 h + transition regression | formal integer-time transition T/C max `1.5538e-5/3.1402e-9`；explicit `14400.25 s` local probe T `2.2991e-4` | COMPLETED as formal-output regression; full horizon pending | `experiments/EXP-Q2-V2-REGRESSION/` |
| Q2_FREEZE_RUN_V2 | n640/cluster2 full-horizon performance attempt | fresh Run1 stopped near `888 s` simulated time due impractical runtime; no metrics/validation/run2 | ABORTED INCOMPLETE; not a source | `experiments/Q2_FREEZE_RUN_V2/` |
| EXP-Q2-ACC-T-FORMAL | Formal transition output lattice audit | integer seconds `14395..14500`、six radii；T/C L∞ `1.55375452663975e-5/3.1402255240564614e-9`；internal `14400.25` T peak `2.2991211631051556e-4` does not reach integer outputs | PASS；internal probe retained as diagnostic | `experiments/EXP-Q2-ACC-T-FORMAL/` |
| EXP-Q2-ACC-C-FORMAL | Formal early moisture audit with policy comparison | all 21 official radii at `1,2,3,4,5,10,20,30,60,100,300,600,1800 s`；5 s startup policy T/C L∞ `7.116765686987492e-6/1.0270424274150258e-5` | PASS；policy-2 t=3 s exceedance documented | `experiments/EXP-Q2-ACC-C-FORMAL/` |
| EXP-Q2-ACC-LONG-TARGETED | Selected long-horizon accuracy/stability certification | 3–48 h n640 localized reference T/C L∞ `1.2509725024756335e-6/2.987415287369899e-6`; passive/final n160 screen below gate；no n640 full horizon | PASS on declared selected points；targeted, not full-horizon proof | `experiments/EXP-Q2-ACC-LONG-TARGETED/` |

Richardson 规则已加固：旧 production 的 T/C observed p=`1.6685/3.0631` 不被直接用于乐观外推；整改表中的 fine/coarse 数字均标为 raw difference 或 conservative bound。完整 V2 full-horizon accuracy confirmation 尚未建立。
本轮正式证书已改为 `experiments/Q2_ACCURACY_REMEDIATION/accuracy_confirmation_v3.json`：它只认证声明的 formal output scope，不把 n=640 局部参考写成 full-horizon replay，也不建立 production result source。

## Q3/Q4 Parallel Production Candidate（2026-09-12）

Q2 final、`A题/`、`src/q1/`、`src/q2/` 保持只读。本阶段生成 Q3/Q4 candidate，不写 final，不 push；Q3/Q4 的模型与输出应在人工 freeze approval 后才可成为 final 交付。

| Experiment | Purpose | Key Config / Scope | Key Result | Status | Evidence |
|---|---|---|---|---|---|
| Q3_PRODUCTION | 固定半径 Q3 阈值定位与 result3/Table5 | 读取 Q2 V3 Run1 raw official lattice；21 个半径；常规输出 `60 s`；Q2 `t=206935/206936 s` 粗夹逼；局部 BE/Picard `1/1024 s` | `Cmax(206935)=0.1500000658293865`，`Cmax(206936)=0.14999977460230157`；首次严格低于端点 `t3=206935.2265625 s=57.4820073785 h`；critical `r=0.0 cm`；全 21 节点端点均低于阈值 | CANDIDATE PASS | `experiments/Q3_PRODUCTION/`、`deliverables/candidate/result3.xlsx` |
| Q4_PRODUCTION | 收缩半径 Q4 动态求解与 result4/Table6 | Appendix 4；Attachment 2 PCHIP；`ξ=r/R(t)`；uniform `n=96`；BE/Picard `dt=4 s`；输出 `60 s`；超出当前半径的物理位置留空 | 粗夹逼 `[191096,191100] s`；`t4=191097.7336093787 s=53.0827037804 h`；`R(t4)=1.2 cm`；critical `ξ=0`；PCHIP 节点误差 `0`；外域伪值 `0` | CANDIDATE PASS | `experiments/Q4_PRODUCTION/`、`deliverables/candidate/result4.xlsx` |
| Q3_Q4_CANDIDATE | 统一 hash/交付清单 | workbook、Table5/6、Fig5-12…18、metrics 和 paper mirrors | candidate validation PASS；figures `7/7`，PNG ≥300 dpi；result3 `3450×22`，result4 `3186×22`；无公式、四位小数格式 | COMPLETE / HUMAN FREEZE PENDING | `experiments/Q3_Q4_CANDIDATE/manifest.json`、`deliverables/candidate/Q3_Q4_VALIDATION.json` |

Q3 endpoint 的 `t3` 使用局部求解的第一个严格低于阈值子步时刻；连续根估计 `206935.2260985608 s` 仅作为 audit 字段。Q4 同理保留粗夹逼和局部细化证据。Q3/Q4 均未把候选数值登记为论文 `VERIFIED` 主张。

## Q2 Chinese Publication Figure Localization（2026-09-12）

这是独立于 Q2 数值冻结的 publication figure 处理实验。未重新运行 Q2 solver，未读取或修改 `src/q2/`，未保存、格式化或改写 `deliverables/final/result2.xlsx`，也未覆盖 `deliverables/final/figures/q2/` 原冻结图。绘图程序只读取现有 `figures/q2/data/` 中的 8 组 CSV/NPZ 图源数据，并把中文版本写入独立目录 `deliverables/final/paper/figures/q2/`。

| Experiment | Purpose | Source / Configuration | Result | Status | Evidence |
|---|---|---|---|---|---|
| Q2_CHINESE_FIGURE_LOCALIZATION | 将 Q2 全部论文图的标题、坐标轴、图例、色标和诊断标签中文化 | frozen Q2 postprocess CSV/NPZ；Matplotlib `Microsoft YaHei`；`axes.unicode_minus=False`；无平滑、无数值插值、无 error clip；PNG requested `300.1 DPI` | 11/11 figure groups；PNG `11/11`；SVG `11/11`；PNG `11/11 >=300 DPI`（写入值 `300.101`）；source numeric arrays/x/y/sampling trace `11/11`；中文 text `11/11`；result2 SHA before/after/current 均为 `84fb32457193e158debdf569d34f5f41b97e78496b30dd9b2e134385439e10da` | COMPLETED / NUMERIC FREEZE UNCHANGED | `experiments/Q2_CHINESE_FIGURE_LOCALIZATION/validation.json`、`deliverables/final/paper/figures/q2/Q2_CHINESE_FIGURE_MANIFEST.json` |

Q1/Q3/Q4 只做了一次 paper-figure metadata 检查，没有数值重算或重画：Q1 manifest 未发现明显英文标题，Q3/Q4 现有 label source 未发现明显英文描述标签；`PCHIP`、`Cmax`、`R(t)`、`t3/t4` 保留为算法或数学记号。Q1 的 `pointwise error zero-crossing / cancellation dip` 解释不变。

Q2 中文 publication figure freeze 与 Q2 numerical/result freeze 分开记录；原 `deliverables/final/figures/q2/` 文件哈希通过对照且未被覆盖。Q3/Q4 候选 final-freeze audit 同步完成，但仍等待人工批准，不把候选工作簿复制到 final。

## Q3/Q4 Joint Final Freeze（2026-09-12）

人工授权已批准 Q3/Q4 联合最终冻结。本阶段不重跑 Q3/Q4 solver；仅对已验证 candidate 做官方交付契约修正、byte-copy 和最终资产登记。精确事件时刻保留在论文 Table5/6 与 freeze audit，不写入严格 60 s workbook lattice。

| Item | Result | Evidence |
|---|---|---|
| Q3 event proof | PASS；`t3=206935.2265625 s`，最终局部 bracket 宽度 `0.0009765625 s`，critical `r=0.0 cm` | `experiments/Q3_PRODUCTION/validation.json`、`docs/Q3_FINAL_FREEZE_AUDIT.md` |
| Q4 event proof | PASS；`t4=191097.7336093787 s`，局部细化分辨率 `0.0625 s`，`R(t4)=1.2 cm`，critical `ξ=0` | `experiments/Q4_PRODUCTION/validation.json`、`docs/Q4_FINAL_FREEZE_AUDIT.md` |
| Official workbooks | Q3 `3449×22`、Q4 `3185×22`；严格 60 s lattice；无公式、无 NaN/Inf、四位小数 | `deliverables/final/Q3_MANIFEST.json`、`deliverables/final/Q4_MANIFEST.json` |
| Tables | Table5 trace `77/77`；Table6 trace `90/90` | `deliverables/final/paper/tables/` |
| Figures | Q3 `3/3`、Q4 `4/4`、comparison `1/1`；PNG ≥300 DPI | `deliverables/final/paper/PAPER_ASSET_MANIFEST.json` |
| Freeze audit | `FINAL_FREEZE_COMPLETE / APPROVED` | `experiments/Q3_Q4_CANDIDATE/final_freeze_audit.json` |

Q3/Q4 final paper asset整理与数值冻结分开留痕；历史失败实验保留，未 push 远程。

## Q3/Q4 Independent Verification Addendum（2026-09-13）

本轮在已冻结数值资产之外新增独立审计实现，不修改 Q2 solver、冻结工作簿或官方源。Q3 独立扫描和局部细化通过；Q4 独立 n=96/dt=4 复现冻结 production，但 n=144/dt=2 的事件时刻为 `52.830168163752184 h`，与冻结 `53.08270378038297 h` 不满足四位小时稳定性，因此 Q4 独立验证标记 `HOLD`，不自动替换 Q4 final。

| Experiment | Purpose | Key Config | Result | Status | Evidence |
|---|---|---|---|---|---|
| Q34_INDEPENDENT_AUDIT | 独立扫描 Q3 raw、独立 Q3 局部细化、Q4 moving-domain/FVM 方程审计、恒半径回归、PCHIP/linear 半径比较、Q4 网格/时间精化、守恒/Robin/Table6 审计 | Q3 raw 全时域；Q3 `n=20/40, dt=1/1024 s` 局部；Q4 `n=48/8, 96/4, 144/2` 从 `t=0`；线性半径 `n=48/8` 对照 | Q3 `PASS`；Q4 production reproduction `PASS`，但 finer round4 `52.8302` vs frozen `53.0827`，Q4 `HOLD`；恒半径 regression `PASS`，表面/外域 `PASS` | COMPLETED / Q4 HUMAN REVIEW | `experiments/Q34_INDEPENDENT_AUDIT/`、`docs/Q34_INDEPENDENT_AUDIT.md` |

## Q4 Numerical Convergence Finalization（2026-09-13）

依据新的人工授权，仅补足 Q4 时间/空间误差分离和最小必要 refinement；不重做已通过审计，不修改 `src/q4/` 或任何 final 数值资产。A/B/C/D 均由独立实现从 `t=0` 运行，随后按 `SPATIAL DOMINANT` 只运行 `n=192, dt=2 s`，并在事件跨越步内细化 root 到 `0.0625 s`。

| Experiment | Purpose | Key Config | Result | Status | Evidence |
|---|---|---|---|---|---|
| Q4_CONVERGENCE_FINAL | 分离时间误差、空间误差、事件根定位误差，并按主导误差选择最小下一层 | A `96/4`；B `96/2`；C `144/4`；D `144/2`；E `192/2`；全为独立 fresh `t=0` | `Δtime≈4.8 s`，`Δspace(A→D)≈904.3 s`；空间/时间约 `188.0`；E=`52.7509055656 h`，细层 D→E=`0.0792625982 h`；保守不确定度=`0.0806158781 h` > `0.00005 h` | COMPLETED / Q4 HOLD | `experiments/Q4_CONVERGENCE_FINAL/q4_error_decomposition.json`、`docs/Q4_CONVERGENCE_FINAL.md` |
| Q4_INTERPOLATION_SENSITIVITY_FINAL | 在选定层级比较半径插值 | `n=192, dt=2 s`；PCHIP 与 linear；root 子步 `0.0625 s` | PCHIP=`52.7509055656 h`，linear=`52.7569423508 h`，差=`21.7324 s`；保留 PCHIP | COMPLETED / SENSITIVITY ONLY | `experiments/Q4_CONVERGENCE_FINAL/interpolation_sensitivity_n192_dt2.json` |

## Q4 Spatial Convergence Extrapolation（2026-09-13）

空间收敛 gate 在固定 `dt=2 s` 下新增 F/G/H 三次 fresh-from-`t=0` 运行。非等比网格使用直接三参数 `t(n)=t_inf+a*n^(-p)` 拟合；不使用等比 Richardson 简化公式。Triplet 外推极限仍漂移，Q4 保持 HOLD，不创建 corrected candidate。

| Experiment | Purpose | Key Config | Result | Status | Evidence |
|---|---|---|---|---|---|
| Q4_SPATIAL_CONVERGENCE_FINAL | 建立连续空间极限并检查 triplet 稳定性 | `dt=2 s`；B/D/E/F/G/H=`n=96/144/192/256/320/384`；均 fresh `t=0` | `t_inf`: `52.6657612843`、`52.6617656682`、`52.6601718696`、`52.6594537782 h`；最近差 `0.0007180914 h` > `0.00005 h`；p 仍漂移 | COMPLETED / Q4 HOLD | `experiments/Q4_SPATIAL_CONVERGENCE_FINAL/`、`docs/Q4_SPATIAL_CONVERGENCE_FINAL.md` |

## Q4 Final Asymptotic Certification（2026-09-13）

最终 gate 完成指定的 `n=512,dt=2 s` 和 `n=384,dt=1 s`，并以实际数据比较 free-p、fixed-p=2、p=2+n^-3。空间外推方法包络及 n=512 到 continuum 的关系仍使保守数值不确定度约 `0.0169296323 h`（含时间/root），高于 `21.7324 s` 插值敏感性；Q4 保持 HOLD，不创建 corrected candidate。

| Experiment | Purpose | Key Config | Result | Status | Evidence |
|---|---|---|---|---|---|
| Q4_FINAL_ASYMPTOTIC_CERTIFICATION | 最终空间/时间渐近认证和连续极限审计 | spatial `dt=2`，n=`96..512`；temporal `n=384,dt=1`；free-p/fixed-p2/p2+n^-3 | spatial estimate=`52.6588571833 h`；time-corrected audit estimate=`52.6575227799 h`；total uncertainty=`60.9467 s`；空间阶仍漂移 | COMPLETED / FINAL HOLD | `experiments/Q4_FINAL_ASYMPTOTIC_CERTIFICATION/`、`docs/Q4_FINAL_ASYMPTOTIC_CERTIFICATION.md` |

## Q4 Deadline Fast-Final（2026-09-13）

根据新的人工 deadline gate，完成 K/L 两次 fresh-from-`t=0` 生产运行；不改变 `src/q4/` 算法、边界、插值或时间步。I→K→L 事件时刻单调下降，按 gate 使用 L 作为直接论文生产结果。此前 `Q4_FINAL_ASYMPTOTIC_CERTIFICATION` 的 HOLD 保留为历史审计，不伪装成当前生产来源。

| Experiment | Purpose | Key Config | Result | Status | Evidence |
|---|---|---|---|---|---|
| Q4_PAPER_FINAL_N640 | K 支持性空间趋势确认 | `n=640, dt=2 s`；fresh `t=0`；minimal diagnostics | `t4=189599.04773429973 s=52.6664021484 h`；`R=1.2 cm`；center；max Robin=`6.4203e-7`；max Picard=`6` | COMPLETED | `experiments/Q4_PAPER_FINAL_N640/` |
| Q4_PAPER_FINAL_N768 | L 论文生产原始数据 | `n=768, dt=2 s`；fresh `t=0`；60 s samples + exact event + full snapshots | `t4=189590.53534526424 s=52.6640375959 h`；`R=1.2 cm`；center；max Robin=`5.4413e-7`；max Picard=`6` | COMPLETED / PAPER FINAL | `experiments/Q4_PAPER_FINAL_N768/` |
| Q4_N768_DELIVERY | 从 L 原始数据生成候选 workbook、Table6、图和 Word/PDF | official 60 s lattice；event only in paper data | result4 `3160×22`；workbook trace `48746/48746`；Table6 `54/54`；4 组图数据 trace `4/4` | PASS / FROZEN | `deliverables/final/Q4_MANIFEST.json`、`deliverables/final/Q4_FREEZE_RECORD.json` |
