# Validation Checklist

本文件是独立验证清单。模型得到较好指标并不等于问题已经解决。

## Workflow Integrity Checks

| 检查项 | 方法 | 结果 | 证据 | 状态 |
|---|---|---|---|---|
| 官方资产存在性与可读取性 | `scripts/validate_inputs.py` | 7 个官方资产可读取 | 脚本输出 | PASS |
| 官方资产 SHA-256 | `scripts/validate_inputs.py` | 与 `docs/DATA_CATALOG.md` 一致 | DATA_CATALOG | PASS |
| 官方 Workbook Sheet 与行列骨架 | `scripts/validate_inputs.py` | 附件1/2与4个模板结构一致 | 脚本输出 | PASS |
| 官方结果模板完整性 | `scripts/validate_templates.py` | Sheet、表头、占位时间和数据区空白通过 | 脚本输出 | PASS |
| 官方源文件未被修改 | `git diff -- A题` | 无差异 | Git 状态 | PASS |
| 交付隔离 | 人工检查 `deliverables/README.md` | Q1/Q2 final 均由已验证 candidate COPY ONLY 产生；Q3/Q4 无 final | 交付说明、`deliverables/final/result1.xlsx`、`deliverables/final/result2.xlsx` | PASS |

## PRE-MODELING GATE

| Gate Item | Evidence | Status |
|---|---|---|
| official assets | `scripts/validate_inputs.py` | PASS |
| official SHA | `scripts/validate_inputs.py` | PASS |
| official source git diff clean | `git diff -- A题` | PASS |
| template skeleton validation | `scripts/validate_templates.py` | PASS |
| deliverable contract validation | `scripts/validate_deliverable_contract.py` | PASS |
| environment reproducibility | `.venv`, requirements files, Python 3.12.14 | PASS |
| tests | `pytest -q` | PASS: 32 passed |
| Q1-Q4 registration | `docs/STATE.md`, `config/deliverables.json` | PASS |
| candidate state | `deliverables/candidate/` | Q1/Q2 candidate 均已验证；Q3/Q4 无 candidate | PASS |
| final state | `deliverables/final/` | PASS；Q1/Q2 final 已人工批准并验证，Q3/Q4 无 final |
| experiment scope | `docs/EXPERIMENTS.md`; internal Q1 evidence only after implementation authorization | PASS |
| findings/claims boundary | `docs/FINDINGS.md`, `docs/CLAIMS.md`; no paper claims generated | PASS |
| no generated answers | source/template/result audit | PASS |

`PRE-MODELING GATE = PASS`

Remaining Open Questions are classified by blocking phase in `docs/PROBLEM_SPEC.md`. Modeling questions such as Q4 dynamic-radius synchronization block only `MODEL IMPLEMENTATION`, not this Workflow Gate.

## Q1 MODEL DESIGN GATE

| Gate Item | Evidence | Status |
|---|---|---|
| official Q1 PDF reread | `A题/A题.pdf` text extraction and visual review of pages 1 and 3 | PASS |
| Q1 requirement matrix | `docs/Q1_PLAN.md` | PASS |
| Q1 input data audit | `docs/Q1_PLAN.md`; 241 rows, 60 s interval, no missing/duplicate/non-finite values | PASS |
| result1 template audit | `scripts/validate_templates.py`; two sheets, 5×6 skeleton, blank data area | PASS |
| variable and unit registration | `docs/Q1_PLAN.md` | PASS |
| candidate assumptions | `docs/ASSUMPTIONS.md`; remaining unaccepted high-impact items marked `NEEDS_REVIEW`, OQ-006/OQ-008 separately accepted | PASS |
| candidate models and Baseline | `docs/Q1_PLAN.md`, `docs/DECISIONS.md` | PASS |
| numerical strategy design | `docs/Q1_PLAN.md`; no solver run | PASS |
| validation plan | `docs/Q1_PLAN.md` | PASS |
| experiment plan | `docs/EXPERIMENTS.md`; EXP-001–EXP-007 registered before implementation | PASS |
| no final Q1 result | historical design gate; final output is created only after later approval | PASS |
| Q2/Q3/Q4 unchanged | `docs/STATE.md` | PASS |

`Q1 MODEL DESIGN GATE = PASS`

该 Gate 只表示 Q1 的设计工作包完成，不表示推荐模型已验证，也不授权自动进入正式实现。

## Q1 IMPLEMENTATION & NUMERICAL VALIDATION GATE

| Gate Item | Evidence | Status |
|---|---|---|
| implementation scope | `src/q1/` contains M1 nonlinear-D, M2 constant-D, and M3 boundary comparison; `src/q1/baseline.py` contains B0 | PASS |
| reusable numerical kernel | `src/common/numerics.py`; deterministic Thomas solver and radial grid | PASS |
| implementation tests | `pytest -q` | PASS: 32 passed |
| EXP-001 smoke | `experiments/EXP-001/metrics.json` | PASS |
| EXP-002 B0/M1/M2 comparison | `experiments/EXP-002/metrics.json` | PASS; comparison recorded, no model freeze |
| EXP-003 time sensitivity | `experiments/EXP-003/metrics.json` | PASS; differences decrease under refinement |
| EXP-004 spatial sensitivity | `experiments/EXP-004/metrics.json` | PASS; differences decrease under refinement |
| EXP-005 Robin/Dirichlet sensitivity | `experiments/EXP-005/metrics.json` | PASS; material boundary sensitivity recorded |
| EXP-006 interpolation sensitivity | `experiments/EXP-006/metrics.json` | PASS; material temperature sensitivity recorded |
| EXP-007 conservation/range checks | `experiments/EXP-007/metrics.json` | PASS |
| official source integrity | `git diff -- A题`; official validators | PASS |
| final result isolation | `deliverables/candidate/`, `deliverables/final/` | PASS; Q1 final only, official source untouched |
| Q2/Q3/Q4 boundary | `docs/STATE.md` | PASS; all remain `NOT STARTED` |

`Q1 IMPLEMENTATION & NUMERICAL VALIDATION GATE = PASS`；OQ-005/OQ-006/OQ-007/OQ-008 已分别登记为交付决策、建模假设、数值决策和建模简化。最终结果交付仍须通过下方 `Q1 FINAL NUMERICAL ACCURACY & DELIVERABLE GATE`。

## Q1 FINAL NUMERICAL ACCURACY & DELIVERABLE GATE

| Gate Item | Evidence | Status |
|---|---|---|
| OQ-005/OQ-006/OQ-007/OQ-008 resolution | `docs/DECISIONS.md`、`docs/PROBLEM_SPEC.md` | PASS |
| Q1 output contract freeze | `config/deliverables.json`、`docs/DELIVERABLE_SPEC.md` | PASS（Q1 contract frozen; Q2–Q4 remain open） |
| Full-horizon spatial convergence | `experiments/EXP-Q1-FULL-SPATIAL/metrics.json` | PASS；3 层 cluster base320/640/1280，细层温度 `3.5588e-7 °C`、含水率 `1.2258e-6 kg/kg` |
| Full-horizon temporal convergence | `experiments/EXP-Q1-FULL-TEMPORAL/metrics.json` | PASS；3 层 BDF2 dt `.25/.125/.0625 s`，细层温度 `4.2626e-7 °C`、含水率 `5.5889e-6 kg/kg` |
| Initial-layer full-horizon check | `EXP-Q1-FULL-SPATIAL/metrics.json` | PASS；表面 t=1/10/60/100/300/600/1800 s 均低于门，未出现晚期反弹 |
| Accuracy criterion | `EXP-Q1-FULL-SPATIAL/metrics.json`、`EXP-Q1-FULL-TEMPORAL/metrics.json` | PASS；选定最低成本配置温度 `1.4012e-6 °C`、含水率 `2.7414e-5 kg/kg`，均 `<5e-5` |
| Rounding diagnostics | `criterion_reference` in full-horizon metrics | AUXILIARY；温度 129、含水率 108 个 ambiguous，未用于自动否决 |
| Freeze rerun | `experiments/Q1_FREEZE_RUN/` | PASS；同一配置从零双跑，完整内部场 SHA-256 一致，两个运行验证 PASS |
| Candidate generation | `deliverables/candidate/result1.xlsx` | PASS；仅由 `Q1_FREEZE_RUN/run_1` 源生成 |
| Candidate workbook validation | `scripts/validate_q1_candidate.py`、`experiments/Q1_FREEZE_RUN/candidate_validation.json` | PASS；结构、有限数值、4位 ROUND_HALF_UP、随机20单元格和表1/2各35点均通过 |
| Human audit package | `experiments/Q1_FREEZE_RUN/`、`deliverables/candidate/result1.xlsx` | PASS；`Q1 HUMAN FREEZE APPROVAL = APPROVED` |

## Q1 FINAL FREEZE, VISUALIZATION & HANDOFF GATE

| Gate Item | Evidence | Status |
|---|---|---|
| Human freeze approval | `docs/Q1_FINAL_FREEZE_AUDIT.md`、`deliverables/final/Q1_MANIFEST.json` | PASS；APPROVED |
| Candidate-to-final byte copy | candidate/final SHA-256 | PASS；两者均为 `06b67b1f688d84a701ac4d2f4b0f47a1624069877df6724faf071a48af177b5c` |
| Final workbook validation | `scripts/validate_q1_final.py`、`experiments/Q1_FINAL_FREEZE/final_result1_validation.json` | PASS |
| Figure generation and validation | `figures/q1/FIGURE_MANIFEST.json`、`FIGURE_VALIDATION.json` | PASS；9 figures，纸面点 70/70，随机图表数据点 20/20 |
| Q2 boundary | `docs/STATE.md`、`docs/HANDOFF.md` | PASS；Q2/Q3/Q4 remain `NOT STARTED` |

`Q1 FINAL FREEZE, VISUALIZATION & HANDOFF GATE = COMPLETE`；Q1 已冻结并完成最终交付。不得启动 Q2，除非获得新的明确授权。

## Q1 NUMERICAL CONVERGENCE DIAGNOSIS & REMEDIATION GATE（历史阶段记录）

| Gate Item | Evidence | Status |
|---|---|---|
| implementation audit | `docs/Q1_NUMERICAL_REMEDIATION_AUDIT.md`；`src/q1/model.py`、`src/q1/solver.py` | PASS；中心半体积、内部几何、表面 Robin 行、BE 层级、Picard 和输出对齐均已逐项映射，未发现生产实现缺陷 |
| Level 1 raw convergence | `experiments/EXP-Q1-NUM-DIAG/metrics.json` | PASS as diagnosis；已记录 L∞/mean/RMSE、中心/表面/论文点/全网格及最大位置 |
| Level 2 order/Richardson | `experiments/EXP-Q1-NUM-DIAG/metrics.json` | PASS as diagnosis；空间温度阶约 2，BE 时间阶约 1；含水率的全网格 L∞ 受早期/表面误差主导 |
| Level 3 rounded stability | `EXP-Q1-FINAL-CONV`、`EXP-Q1-NUM-REMEDIATION` | AUXILIARY；BDF2 论文点 `0/35`，但全网格估计安全裕量未全通过 |
| error localization | `experiments/EXP-Q1-NUM-DIAG/*.svg` | PASS；已定位早期时间和表面带为含水率主要误差区域 |
| independent benchmark | `experiments/EXP-Q1-NUM-BENCH/metrics.json` | PASS；BE 空间约二阶、时间约一阶，支持生产离散的基本阶数 |
| Robin/boundary verification | `tests/test_q1_robin_boundary.py`, `pytest -q` | PASS；32 tests passed，含独立 Robin 行、中心几何、BDF2 边界缩放和聚类节点测试 |
| Picard sensitivity | `experiments/EXP-Q1-PICARD-SENS/metrics.json` | PASS；非线性迭代误差远小于离散误差 |
| remediation candidate | `experiments/EXP-Q1-NUM-REMEDIATION/metrics.json` | PARTIAL；BDF2 改善论文点，但未通过全网格保守估计误差门 |
| result workbook generation | `deliverables/candidate/`, `deliverables/final/` | NOT RUN；本阶段明确禁止生成 `result1.xlsx` |
| Q2 boundary | `docs/STATE.md` | PASS；Q2–Q4 仍为 `NOT STARTED` |

`Q1 NUMERICAL REMEDIATION GATE = BLOCKED`。BDF2 仅登记为 `M1-NUM-T2` 候选；不得生成 `result1.xlsx`，不得启动 Q2。

## Q1 INITIAL-LAYER & SURFACE-ACCURACY GATE（历史早期记录；阻塞已由上方全时段复验关闭）

| Gate Item | Evidence | Status |
|---|---|---|
| scope boundary | Latest authorized prompt; Q2/Q3/Q4 unchanged | PASS; Q1 only |
| t=0 temperature compatibility | `EXP-Q1-INITIAL-LAYER/metrics.json` | PASS; residual `-0.0 W/m²` within representation |
| t=0 moisture compatibility | `EXP-Q1-INITIAL-LAYER/metrics.json` | SUPPORTED INITIAL LAYER; residual `-2.024296e-6 m/s`, no physical input changed |
| diffusion-scale diagnostic | `EXP-Q1-INITIAL-LAYER/metrics.json` | PASS as diagnostic; not used as an error theorem |
| surface error decay | `EXP-Q1-SURFACE-DECAY/metrics.json`, signed/absolute raw CSV and plots | PASS as diagnosis; signed error is retained and the 20–40 s near-surface dip is classified as cancellation, not sudden accuracy improvement |
| BDF2 startup comparison | `EXP-Q1-BDF2-STARTUP/metrics.json` | PASS as comparison; early BE substeps not selected |
| clustered-grid manufactured benchmark | `EXP-Q1-CLUSTER-BENCH/metrics.json` | PASS; space about 1.95–1.96 and time about 1.01–1.06 |
| clustered-grid real-Q1 short test | `EXP-Q1-CLUSTER-SHORT/metrics.json` | PASS as candidate evidence; explicit official nodes preserved |
| t=1 reference and uncertainty | `EXP-Q1-CLUSTER-TEMPORAL/metrics.json` | PARTIAL; `C(R,1s)=2.5177587784`, combined surface uncertainty `3.1850e-5 kg/kg` |
| rounding certification | `EXP-Q1-CLUSTER-TEMPORAL/metrics.json` | PARTIAL; 20 certified, 1 ambiguous of 21 official positions |
| full 0–1800 s candidate verification | not run by this gate | BLOCKED; do not generate `result1.xlsx` |
| final-gate re-entry | `docs/Q1_INITIAL_LAYER_AUDIT.md` | BLOCKED; waiting for human review |

`Q1 INITIAL-LAYER & SURFACE-ACCURACY GATE` 的早期阻塞已由后续 `EXP-Q1-FULL-SPATIAL`、`EXP-Q1-FULL-TEMPORAL` 和 `Q1_FREEZE_RUN` 复验关闭；其诊断结论仍保留为支持性证据。Q1 随后已完成人工 freeze approval、final 验证和图表交付；不得启动 Q2，除非获得新的明确授权。

## Q1 EARLY SURFACE SIGNED-ERROR AUDIT（本轮）

| Gate Item | Evidence | Status |
|---|---|---|
| error definition | `experiments/EXP-Q1-SURFACE-DECAY/metrics.json`、`surface_signed_error_15_45s.csv` | PASS；同时保存 `e=C_test-C_ref` 与 `abs(e)`，误差计算使用完整浮点 |
| 15–45 s raw table | `experiments/EXP-Q1-SURFACE-DECAY/surface_signed_error_15_45s.csv` | PASS；1 s 间隔，含 20/25/30/35/40 s，未先四舍五入 |
| signed/absolute plots | `signed_error_vs_time.svg`、`absolute_error_semilogy.svg` | PASS；无 smoothing、无 error interpolation、无 epsilon clip，x/y 对齐检查为 0 |
| boundary and solver trace | `boundary_solver_trace_0_60s.csv`、surface `metrics.json` | PASS；C_inf 单线性段、dt 固定、Picard、非线性/线性残差和时间对齐均有记录 |
| Robin independent check | trace CSV；surface metrics | PASS；surface control-volume residual `3.4778292694089816e-17`，15–45 s 无同步突变 |
| separated time convergence | `experiments/EXP-003/` | PASS as diagnosis；固定 `dr=0.025 cm`，BE 相邻直接差分 observed order 进入约一阶 |
| separated space convergence | `experiments/EXP-004/` | PASS as diagnosis；固定 `dt=0.0625 s`，全局 L∞/L2 随 dr 细化下降，近表面谷值发生移动 |
| final workbook / official source | `deliverables/final/result1.xlsx`、`A题/` | PASS；本轮未修改、未重新生成 |

诊断结论限定为 A：r=1.9 cm 的 signed error 在 35–36 s 穿过 0，绝对误差深谷是 `pointwise error zero-crossing / cancellation dip`；字面 r=2.0 cm 表面在 15–45 s 没有穿零。不得把该深谷作为模型优越性或快速收敛证据。Q2/Q3/Q4 在本轮暂停。

## 通用检查

| 检查项 | 适用问题 | 结果 | 证据 | 状态 |
|---|---|---|---|---|
| 数据泄漏 | 全局 | 尚未检查 | — | TODO |
| 数据划分与交叉验证 | 全局 | 尚未检查 | — | TODO |
| 残差分析 | 视模型而定 | 尚未检查 | — | TODO |
| 异常值影响 | 全局 | 尚未检查 | — | TODO |
| 参数敏感性 | Q1 | 时间步长、网格、边界和插值敏感性已完成 | EXP-003–EXP-006 | PASS（仍需人工解释领域容差） |
| 鲁棒性与稳定性 | Q1 | M1/M2 在验证配置下有限且可收敛 | EXP-001、EXP-003、EXP-004、EXP-007 | PASS（限当前配置） |
| 边界情况 | Q1 | 中心零通量、表面通量方向、非负水分 | 测试、EXP-001、EXP-007 | PASS |
| 与现实常识一致性 | Q1 | 方向和范围 sanity check；未做实测校准 | EXP-007 | PARTIAL |
| Baseline 对比 | Q1 | B0 与 M1/M2 的平均及径向响应对照 | EXP-002 | PASS（不冻结模型） |
| 必要的消融实验 | Q1 | M2 常-D、M3 Dirichlet 对照 | EXP-002、EXP-005 | PASS |

## 验证记录模板

```markdown
## VAL-xxx 标题

问题：Q1/Q2/Q3/Q4
检查项：
方法：
结果：
证据：EXP-xxx / 文件路径
结论：
剩余风险：
状态：PASS / FAIL / PARTIAL / TODO
```

## Q2 MODEL DESIGN & CONTRACT GATE

本节记录 Q2 设计 Gate，而不是 Q2 数值结果 Gate。未实现 solver、未运行正式长时仿真、未生成 `result2.xlsx`。

| 检查项 | 方法/证据 | 状态 |
|---|---|---|
| Official requirements extracted | `docs/Q2_PLAN.md`；官方 PDF 问题2、表3/4、附录3与官方 result2 模板 | PASS |
| Appendix 3 formula and unit verification | 官方 PDF 页面4视觉核对；`scripts/audit_q2_property_spec.py`；`EXP-Q2-PROPERTY-POINTS` | PASS（设计审计） |
| Attachment 1 tail audit | `scripts/audit_q2_environment_tail.py`；`EXP-Q2-ENV-TAIL`；输入只读 | PASS（数据审计） |
| Q1 → Q2 delta matrix | `docs/Q2_PLAN.md` | PASS |
| TEAM_REFERENCE reconciliation | `docs/Q2_PLAN.md`；五份 DOCX 不升级为官方事实 | PASS |
| Q2 physics candidate | Q2-M1 variable-property coupled radial model | PASS（候选设计） |
| Numerical candidate matrix | Q2-NUM-CANDIDATE-A/B/C，未选择最终方案 | PASS（候选设计） |
| Coupled Picard design | 分场归一化残差、更新时序、最大迭代、松弛与 fail-closed | PASS（接口设计） |
| Variable-coefficient FVM audit | 算术/调和平均均保留；未裁决 | OPEN（实现前决策） |
| Environment after 14400 s | `OQ-Q2-ENV-001`；常值候选未确认 | OPEN（人工决策） |
| Environment interpolation | `OQ-Q2-ENV-002`；linear/PCHIP 未选择 | OPEN（人工决策） |
| Q2 end condition | `OQ-Q2-END-001`；不把 Q3 阈值升级为 Q2 官方终点 | OPEN（人工决策） |
| Accuracy criterion | `OQ-Q2-ACC-001`；Q1 `<5e-5` 仅候选起点 | OPEN（实现后验证） |
| Long-horizon architecture | 流式输出、内存/行数估算、checkpoint/restart 契约 | PASS（设计） |
| Validation plan | 属性、单位、极限、边界、守恒、耦合、收敛、重启、Q1 overlap、交付检查 | PASS（计划） |
| Q2 deliverable contract | `docs/Q2_PLAN.md`、`docs/DELIVERABLE_SPEC.md`；终点/行数未冻结 | PASS（草案） |
| Q1 freeze integrity | `git diff -- A题` 为空；Q1 final/figures/audit 未改 | PASS |
| Q2 implementation boundary | `src/q2/` solver、正式结果、Q3/Q4 均未开始 | PASS |

`Q2 MODEL DESIGN & CONTRACT GATE = COMPLETE`；等待人工 Q2 implementation authorization。以上 OPEN 项均已显式登记，不能在实现时静默假设。

## CUMCM Q2 IMPLEMENTATION & SHORT-HORIZON VALIDATION GATE

本阶段依据人工授权执行 Q2 implementation、短时数值验证和0–3 h内部验证；明确不生成 `result2.xlsx`，不启动 Q3/Q4，不决定 Q3 烘干结束时间，也不写 Q2 最终论文结论。

| Gate item | Evidence | Status |
|---|---|---|
| Q1 freeze regression | `git diff -- A题` 为空；Q1 final/reference SHA-256 未变；Q1 tests 仍通过 | PASS |
| Appendix 3 properties and Kelvin | `src/q2/properties.py`、`tests/test_q2_properties.py`、官方 PDF page 4 | PASS |
| Attachment 1 environment | `src/q2/environment.py`；原始点 exact；linear 可执行；PCHIP 因 SciPy 不存在保持 OPEN | PARTIAL_OPEN |
| Variable-coefficient FVM benchmark | `experiments/EXP-Q2-003/metrics.json` | PASS；当前 Robin 节点闭合空间约一阶、BE 时间约一阶 |
| Coupled Picard | `EXP-Q2-001/004/009/011` diagnostics | PASS；所有已运行步骤收敛，双场残差分别记录 |
| 0–60 s smoke | `experiments/EXP-Q2-001/` | PASS |
| 0–1800 s Q1/Q2 overlap | `experiments/EXP-Q2-002/` | PASS；sanity only，Q1/Q2不要求相等 |
| Time convergence | `experiments/EXP-Q2-005/` | PASS；固定 `dr=.025 cm`，observed order 约一阶 |
| Space convergence | `experiments/EXP-Q2-006/` | PASS；固定 `dt=.125 s`，L∞/L2随细化下降 |
| BE/BDF2 | `experiments/EXP-Q2-007/` | PASS；Candidate A BDF2 记为 `RECOMMENDED_FOR_Q2_FREEZE`，不是 FINAL |
| Mass/heat/Robin audit | `experiments/EXP-Q2-009/` | PASS；逐步诊断完整 |
| Checkpoint/restart | `experiments/EXP-Q2-010/` | PASS；共同末场最大差为0 |
| 0–3 h internal validation | `experiments/EXP-Q2-011/` | PASS；0–10800 s，未启用 post-14400 provider |
| result2 protection | candidate/final 下无 `result2.xlsx`；官方 `A题/` 未修改 | PASS |
| Q3/Q4 boundary | `docs/STATE.md`、`docs/HANDOFF.md` | PASS；Q3/Q4仍未启动 |

当前状态：`Q2 IMPLEMENTATION & SHORT-HORIZON VALIDATION COMPLETE / WAITING LONG-HORIZON AUTHORIZATION`。`OQ-Q2-ENV-001/002`、`OQ-Q2-BC-001`、`OQ-Q2-FVM-001`、`OQ-Q2-END-001` 和 `OQ-Q2-ACC-001` 继续保持 OPEN；不得将本阶段的内部 candidate 表格直接转换为官方 `result2.xlsx`。

## CUMCM Q2 LONG-HORIZON BOUNDARY & PRODUCTION CONFIG GATE

本阶段依据新的人工授权执行 0–6 h → 0–24 h → 0–48 h → 0–72 h 分段验证、环境/插值/边界/界面选择证据、低含水率物性、守恒与 Robin 独立复算、被动事件观察、checkpoint/restart、长时收敛和 Q2-B0 控制。所有官方源与 Q1 冻结资产保持只读；未生成 `result2.xlsx`，未启动 Q3/Q4。

| Gate item | Evidence | Status |
|---|---|---|
| Environment tail statistics and transition | `EXP-Q2-012-ENVIRONMENT/metrics.json` | PASS as audit；ENV-A last raw 与 tail40 mean 的输入/场差异已量化；OQ-ENV-001 OPEN |
| Linear/PCHIP implementation and comparison | `EXP-Q2-013-INTERPOLATION/metrics.json` | PASS as comparison；两者精确复现 knots，但输出差异非忽略；OQ-ENV-002 OPEN |
| h/hm carryover sensitivity | `EXP-Q2-014-BC-SENSITIVITY/metrics.json` | PASS as sensitivity；h 低影响、hm 中等影响；OQ-BC-001 OPEN |
| Arithmetic/harmonic face mean | `EXP-Q2-015-INTERFACE-MEAN/metrics.json` | PASS；真实运行差异很小且 benchmark 通过；arithmetic 仅为低成本 provisional recommendation |
| 0–72 h ENV-A long run | `EXP-Q2-016-LONG-ENV-A-last-raw/` | PASS with recovered output artifact；所有 stage 有限/正，最终 Picard `2/2/2/2`，不触发 Q3 停止 |
| 0–72 h ENV-B comparator | `EXP-Q2-016-LONG-ENV-B-tail40-mean/` | PASS as comparator；不能据此静默关闭环境 OQ |
| Low-C diffusivity and property range | long stage JSON/diagnostics | PASS；最终 `D_min=2.6499e-12 m²/s`，未出现非有限或负含水率 |
| Mass/heat/Robin residual | long diagnostics and stage summaries | PASS；最终阶段 mass `2.34e-11`、heat `1.78e-10 J`；Robin residuals separately retained |
| Passive event observer | long stage summaries | PASS as observer；`C<0.15` bracket=`205913–205913.25 s`，不定义 Q2 endpoint |
| Time/space long convergence | `EXP-Q2-017-LONG-CONVERGENCE/` | PASS as long stability evidence；proxy orders与短时正式 order 分开记录 |
| ENV-A/B checkpoint comparison | `EXP-Q2-018-ENV-COMPARISON/` | PASS as decision evidence；6/24/48/72 h differences non-negligible |
| 12 h checkpoint → 24 h restart | `EXP-Q2-019-LONG-RESTART/` | PASS；temperature/moisture final field differences both `0.0` |
| Q2-B0 finite-cost control | `EXP-Q2-020-BASELINE/` | PASS as control；成本更低但 6 h moisture difference `0.392241 kg/kg`，不可替代 coupled model |
| Output sampler integrity | `EXP-Q2-016.../output_recovery_metrics.json` | PASS after recovery；raw duplicate files retained, recovered 1 s grid is complete |
| Q1/A题/result2/Q3/Q4 boundary | `docs/STATE.md`、`docs/HANDOFF.md`、source hashes | PASS；Q1 frozen，`A题/` unchanged，无 `result2.xlsx`，Q3/Q4 NOT STARTED |

长时门结论：数值验证包完成，Q2 生产候选可供人工审核；`OQ-Q2-ENV-001/002`、`OQ-Q2-BC-001`、`OQ-Q2-FVM-001`、`OQ-Q2-END-001` 和 `OQ-Q2-ACC-001` 不因本轮运行而自动关闭。推荐候选为 ENV-A last raw point 后常值、linear、arithmetic face mean、Q1-carried h/hm、内部稳定性窗口至72 h，但仍需人工冻结和单独的 Q2 production/result authorization。

`Q2 LONG-HORIZON BOUNDARY & PRODUCTION CONFIG GATE = COMPLETE / WAITING FOR Q2 PRODUCTION & RESULT AUTHORIZATION`

## Q2 HUMAN MODEL-DECISION FREEZE GATE（2026-09-11）

| Gate item | Evidence | Status |
|---|---|---|
| D1 post-14400 environment | `EXP-Q2-012` tail/transition；`EXP-Q2-018` A/B checkpoints | COMPLETE AS EVIDENCE / HUMAN DECISION PENDING |
| D2 linear/PCHIP | `EXP-Q2-013` exact knots、Table 3/4 points、0–4 h field/flux difference | COMPLETE AS EVIDENCE / HUMAN DECISION PENDING |
| D3 h/hm posture | `EXP-Q2-014` + `EXP-Q2-021` 3 h/72 h targeted screen | COMPLETE AS EVIDENCE / HUMAN DECISION PENDING |
| D4 interface mean | `EXP-Q2-015` benchmark/0–3 h + `EXP-Q2-021` long target | COMPLETE AS EVIDENCE / HUMAN DECISION PENDING |
| D5 Q2 accuracy criterion | packet field/L∞/L2/order/reporting/event separation | PROPOSED / HUMAN DECISION PENDING |
| D6 production horizon | packet passive bracket + safety-tail rule, storage/runtime estimate | PROPOSED / HUMAN DECISION PENDING |
| D7 canonical lineage | `Q2_CANONICAL_DATA_MANIFEST.json` + fail-closed loader tests | COMPLETE AS EVIDENCE / HUMAN DECISION PENDING |

本 Gate 的完成条件是 decision packet、量化证据和 lineage guard 完整，不能等同于
Agent 自动完成模型冻结。`result2.xlsx`、candidate/final workbook 均不存在；Q3/Q4
仍未启动；Q1 保持冻结。

## CUMCM Q2 HUMAN PRODUCTION FREEZE RUN & RESULT CANDIDATE GATE（2026-09-12）

| Gate item | Evidence | Status |
|---|---|---|
| Human production freeze approval | latest user authorization | PASS；配置冻结 |
| Frozen config and baseline capture | `docs/Q2_PRODUCTION_FREEZE.md`、`config.json`、preflight | PASS |
| Fresh production Run1/Run2 | `metrics.json` | PASS；均从 `t=0` 到 `228635 s` |
| Deterministic raw/sampled/diagnostic/checkpoint output | `determinism.json`、`output_hashes.json` | PASS；byte/hash identical |
| Environment transition assertion | `environment.json` | PASS as assertion；发现真实 `14400 s` jump |
| Field/Picard/property/mass/heat/Robin/center checks | `run_1/metrics.json`、`diagnostics_1s.csv` | PASS |
| Temporal/spatial full-region accuracy | `accuracy_confirmation.json`、by-time CSV | FAIL；T/C L∞=`1.9082e-4/2.0357e-4` |
| Candidate result2 structure/format/rounding/traceability | `scripts/validate_q2_candidate.py` | NOT RUN；fail-closed |
| Q2 figures and manifest | `scripts/generate_q2_figures.py` | NOT RUN；fail-closed |
| Q1/A题 integrity | `git diff -- A题`、Q1 hashes | PASS |
| Q3/Q4 boundary | `docs/STATE.md`、`docs/HANDOFF.md` | PASS；仍 NOT STARTED |

结论：`Q2 PRODUCTION CONFIG FROZEN; ACCURACY GATE FAILED; RESULT CANDIDATE BLOCKED`。不得生成 candidate/final result2，不得把 passive event bracket 写成 Q3 最终烘干时间；数值整改已获授权，但尚未完成 V2 full-horizon gate。

## CUMCM Q2 NUMERICAL ACCURACY REMEDIATION GATE（历史起始状态，2026-09-12）

| Gate item | Evidence | Status |
|---|---|---|
| Original raw metric audit | `docs/Q2_ACCURACY_REMEDIATION.md`、old `accuracy_confirmation.json` | PASS；空间/时间 raw difference 分开报告，未称 Richardson uncertainty |
| Richardson rule hardening | remediation metrics and notes | PASS；不使用旧 `p=3.0631` 乐观外推，保留 fine/coarse bound |
| Q2 initial Robin compatibility | `EXP-Q2-ACC-C-INITIAL` | COMPLETED；不相容性仅归类为数值初始层发现 |
| Environment transition BDF2 diagnosis | `EXP-Q2-ACC-T-TRANSITION` | PASS as local evidence；BE restart 残差/Picard 未恶化 |
| Spatial isolation | `EXP-Q2-ACC-SPATIAL*`、cluster3 study | PASS as short evidence；fixed dt，细化 raw L∞下降 |
| Temporal isolation | `EXP-Q2-ACC-TEMPORAL*` | PASS as short evidence；fixed space，细化 raw L∞下降并记录 observed order |
| Early-time policy | `EXP-Q2-NUM-REMEDY-C-TIME` | PASS as short evidence；无物理输入修改 |
| 0–3 h + 14500 s V2 regression | `EXP-Q2-V2-REGRESSION` | PARTIAL；formal integer points低于门槛，但 `14400.25 s` local T probe=`2.2991e-4 °C` |
| V2 full-horizon fresh double run | `Q2_FREEZE_RUN_V2/ABORTED_ATTEMPT.json` | BLOCKED；n640 attempt因运行成本中止，无Run2/完整accuracy confirmation |
| Full-horizon `accuracy_confirmation_v2.json` | none | NOT ESTABLISHED；不得伪造 PASS |
| result2/Q2 figures/Q3/Q4 | candidate/final、Q3/Q4 | BLOCKED / NOT STARTED |

详细整改报告见 `docs/Q2_ACCURACY_REMEDIATION.md`。本节记录 formal scope 修正前的起始阻塞状态；当前状态见下节。

## CUMCM Q2 FORMAL-OUTPUT ACCURACY CERTIFICATION GATE（2026-09-12）

| Gate item | Evidence | Status |
|---|---|---|
| D-Q2-ACCURACY-SCOPE | `docs/DECISIONS.md`、v3 certificate | PASS；formal lattice 与 internal probes 分离 |
| Transition integer output lattice | `EXP-Q2-ACC-T-FORMAL/comparison.csv` | PASS；T/C L∞=`1.55375452663975e-5`/`3.1402255240564614e-9` |
| Transition internal probes | same experiment | PASS as diagnostic；`14400.25 s` T peak=`2.2991211631051556e-4`，未传播至 integer outputs |
| Early official lattice | `EXP-Q2-ACC-C-FORMAL/comparison.csv` | PASS；T/C L∞=`7.116765686987492e-6`/`1.0270424274150258e-5` |
| Selected long-horizon points | `EXP-Q2-ACC-LONG-TARGETED/` | PASS；3–48 h n640 localized reference，passive/final n160 screen |
| No late error growth | targeted by-time metrics + old 0–72 h evidence | PASS on declared selected points；未声称 n640 full horizon |
| Picard / mass / heat / finite field | case diagnostics and metrics | PASS；all complete cases finite，Picard bounded，residuals recorded |
| Q2 V3 production run | no production attempt in this turn | WAITING FOR HUMAN AUTHORIZATION |
| result2/Q2 formal production figures | candidate/final | NOT GENERATED；fail-closed until V3 authorization |
| Q1/Q3/Q4 boundary | `docs/STATE.md`, `docs/HANDOFF.md` | PASS；Q1 frozen，Q3/Q4 not started |

当前结论：`Q2 FORMAL-OUTPUT ACCURACY GATE COMPLETE / WAITING FOR Q2 V3 FREEZE RUN AUTHORIZATION`。证书不是 n=640 full-horizon proof，也不是 `result2.xlsx` 的生产来源；在 V3 授权前不得生成 result2 或启动 Q3/Q4。

## CUMCM Q2 V3 PRODUCTION FREEZE RUN & RESULT CANDIDATE GATE（2026-09-12）

| Gate item | Evidence | Status |
|---|---|---|
| V3 frozen config/baseline/environment/input | `experiments/Q2_FREEZE_RUN_V3/config.json`、`code_hashes.json`、`environment.json`、`input_hashes.json` | PASS |
| Formal accuracy basis | `experiments/Q2_ACCURACY_REMEDIATION/accuracy_confirmation_v3.json` | PASS on declared formal lattice/selected points；not full-horizon n640 proof |
| Fresh Run1/Run2 | `experiments/Q2_FREEZE_RUN_V3/metrics.json` | PASS；both t=0, no reuse |
| Passive bracket and horizon | V3 metrics/config | PASS；`[206935.0,206935.25] s` → `228536 s` |
| Full deterministic outputs | `determinism.json`、`output_hashes.json` | PASS；raw/sampled/diagnostics byte/hash identical |
| Picard/finite fields/mass/heat/Robin/time-step residual | `run_1/metrics.json`、`diagnostics_1s.csv` | PASS；0 non-converged steps |
| Official sampler | V3 official source and metrics | PASS；integer t=1..228536, 21 radii; raw retains t=0 |
| Canonical lineage | `experiments/Q2_CANONICAL_DATA_MANIFEST.json`、`lineage.json` | PASS；Run1 only production canonical |
| Result2 workbook | `candidate_validation.json` | PASS；two sheets, 4 decimals, no formulas, 100/100 random, 60/60 Table3/4 |
| Q2 figures | `figures/q2/FIGURE_MANIFEST.json`、`figure_validation.json` | PASS；11 figure groups, PNG≥300 dpi + SVG, 30/30 trace |
| Q1/A题 integrity | `validation.json`、preflight hashes | PASS |
| Q3/Q4 boundary | `STATE.md`、`HANDOFF.md`、V3 validation | PASS；not started |

上述为 V3 candidate gate 在人工 final freeze 前的历史结论；Q1 20–40 s 深谷仍只可写成 signed-error zero-crossing/cancellation dip。当前 final freeze 结论见下节。

## CUMCM Q2 V3 FINAL FREEZE（2026-09-12）

| Gate item | Evidence | Status |
|---|---|---|
| Human freeze approval | `Q2 V3 production freeze = APPROVED` | PASS |
| Candidate → final workbook | COPY ONLY；candidate/final SHA-256 identical；两者均 `30,303,454` bytes | PASS |
| Final workbook structure | 两张表均 `228537×22`；无公式；数据区 `0.0000` | PASS |
| Workbook trace | random trace `100/100`；Table3/4 `60/60` | PASS |
| Final figures | 11 组、22 个 PNG/SVG；PNG ≥300 dpi；source/final hash identical | PASS |
| Figure trace | `30/30`；无 smoothing、无 numeric interpolation | PASS |
| Run lineage | Run1/Run2 独立从 `t=0`；raw/sampled/diagnostics byte/hash identical | PASS |
| Passive interval / horizon | `[206935.0,206935.25] s`；`228536 s` | PASS |
| Full test suite | `pytest -q` | PASS: 56 passed |
| Protected paths and boundary | `A题/`、`src/q2/` unchanged；Q1 frozen；Q3/Q4 not started | PASS |

最终记录：`experiments/Q2_FINAL_FREEZE/freeze_record.json`；final manifest：`deliverables/final/Q2_MANIFEST.json`。

## CUMCM Q3/Q4 PARALLEL PRODUCTION CANDIDATE GATE（2026-09-12）

| Gate item | Evidence | Status |
|---|---|---|
| Q2/Q1 protection | frozen Q2 SHA、`git diff -- A题 src/q1 src/q2 deliverables/final/result2.xlsx` | PASS；protected inputs/final unchanged |
| Q3 threshold scan | `Q3_PRODUCTION/q3_summary.json`、raw 1 s/21-radii stream | PASS；`206935` 未满足、`206936` 满足，critical `r=0.0 cm` 为扫描结果 |
| Q3 endpoint refinement | Q3 summary `endpoint_refinement` | PASS；局部 BE/Picard 首个 strict-below `t3=206935.2265625 s`，非两 Excel 行线性插值 |
| Q3 result3 overlap | `q3_result3_matrix_full_precision.csv`、candidate workbook | PASS；3448/3448 regular rows traced to frozen Q2 raw source |
| Q3 Table5/figures | candidate tables、`fig_5_12..fig_5_14.*` | PASS；Table5 6 h rows + actual t3；3/3 figure pairs，PNG ≥300 dpi |
| Q4 Appendix 4 properties | `src/q4/properties.py`、`Q4_PRODUCTION/q4_summary.json` | PASS；公式、单位和 Kelvin temperature explicit |
| Q4 Attachment 2 radius | `src/q4/radius.py`、`validation.json` | PASS；PCHIP node error `0`，monotone，post-tail hold recorded |
| Q4 material-coordinate mapping | `src/q4/model.py`、result4 candidate | PASS；ξ=r/R(t)，surface separate，outside-domain blanks `0` violations |
| Q4 threshold/endpoint | `Q4_PRODUCTION/q4_summary.json` | PASS；`[191096,191100] s` → `t4=191097.7336093787 s`，`R(t4)=1.2 cm`，critical ξ=0 |
| Q4 mass/Robin/solver sanity | Q4 summary | PASS as candidate diagnostics；mass normalized max `3.4553928505477293e-4`，Robin max `4.5474756348265686e-7`，constant-R regression finite |
| Workbooks | `scripts/validate_q3_q4_candidates.py` | PASS；result3 `3450×22`、result4 `3186×22`、no formulas、numeric format `0.0000` |
| Unified paper package | `deliverables/candidate/paper/`、candidate manifest | PASS；Table5/6、Fig5-12…18、q3/q4 summary/comparison present |
| Full test suite | `pytest -q` | PASS: `60 passed` |

当前状态：`Q3 = CANDIDATE COMPLETE`、`Q4 = CANDIDATE COMPLETE`、`WAITING FOR HUMAN Q3/Q4 FREEZE APPROVAL`。Q3/Q4 candidate 未进入 final；Q1/Q2 保持冻结；不 push。
