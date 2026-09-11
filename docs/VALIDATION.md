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
| 交付隔离 | 人工检查 `deliverables/README.md` | candidate/final 已建立，当前无结果文件 | 交付说明 | PASS |

## PRE-MODELING GATE

| Gate Item | Evidence | Status |
|---|---|---|
| official assets | `scripts/validate_inputs.py` | PASS |
| official SHA | `scripts/validate_inputs.py` | PASS |
| official source git diff clean | `git diff -- A题` | PASS |
| template skeleton validation | `scripts/validate_templates.py` | PASS |
| deliverable contract validation | `scripts/validate_deliverable_contract.py` | PASS |
| environment reproducibility | `.venv`, requirements files, Python 3.12.14 | PASS |
| tests | `pytest -q` | PASS: 29 passed |
| Q1-Q4 registration | `docs/STATE.md`, `config/deliverables.json` | PASS |
| candidate empty | `deliverables/candidate/` | PASS |
| final empty | `deliverables/final/` | PASS |
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
| no final Q1 result | no `result1.xlsx` candidate/final output; internal evidence is isolated | PASS |
| Q2/Q3/Q4 unchanged | `docs/STATE.md` | PASS |

`Q1 MODEL DESIGN GATE = PASS`

该 Gate 只表示 Q1 的设计工作包完成，不表示推荐模型已验证，也不授权自动进入正式实现。

## Q1 IMPLEMENTATION & NUMERICAL VALIDATION GATE

| Gate Item | Evidence | Status |
|---|---|---|
| implementation scope | `src/q1/` contains M1 nonlinear-D, M2 constant-D, and M3 boundary comparison; `src/q1/baseline.py` contains B0 | PASS |
| reusable numerical kernel | `src/common/numerics.py`; deterministic Thomas solver and radial grid | PASS |
| implementation tests | `pytest -q` | PASS: 29 passed |
| EXP-001 smoke | `experiments/EXP-001/metrics.json` | PASS |
| EXP-002 B0/M1/M2 comparison | `experiments/EXP-002/metrics.json` | PASS; comparison recorded, no model freeze |
| EXP-003 time sensitivity | `experiments/EXP-003/metrics.json` | PASS; differences decrease under refinement |
| EXP-004 spatial sensitivity | `experiments/EXP-004/metrics.json` | PASS; differences decrease under refinement |
| EXP-005 Robin/Dirichlet sensitivity | `experiments/EXP-005/metrics.json` | PASS; material boundary sensitivity recorded |
| EXP-006 interpolation sensitivity | `experiments/EXP-006/metrics.json` | PASS; material temperature sensitivity recorded |
| EXP-007 conservation/range checks | `experiments/EXP-007/metrics.json` | PASS |
| official source integrity | `git diff -- A题`; official validators | PASS |
| final result isolation | `deliverables/candidate/`, `deliverables/final/` | PASS; no `result1.xlsx` generated |
| Q2/Q3/Q4 boundary | `docs/STATE.md` | PASS; all remain `NOT STARTED` |

`Q1 IMPLEMENTATION & NUMERICAL VALIDATION GATE = PASS`；OQ-005/OQ-006/OQ-007/OQ-008 已分别登记为交付决策、建模假设、数值决策和建模简化。最终结果交付仍须通过下方 `Q1 FINAL NUMERICAL ACCURACY & DELIVERABLE GATE`。

## Q1 FINAL NUMERICAL ACCURACY & DELIVERABLE GATE

| Gate Item | Evidence | Status |
|---|---|---|
| OQ-005/OQ-006/OQ-007/OQ-008 resolution | `docs/DECISIONS.md`、`docs/PROBLEM_SPEC.md` | PASS |
| Q1 output contract freeze | `config/deliverables.json`、`docs/DELIVERABLE_SPEC.md` | PASS（Q1 contract frozen; Q2–Q4 remain open） |
| Full output-grid convergence | `experiments/EXP-Q1-FINAL-CONV/metrics.json` | BLOCKED；N160→N320 后温度 1398/37800、水分 4468/37800 个四位小数差异 |
| Paper-point convergence | `experiments/EXP-Q1-FINAL-CONV/metrics.json` | BLOCKED；N160→N320 温度 1/35、水分 4/35；dt1→dt0.25 温度 33/35、水分 7/35 |
| Time-step convergence at selected spatial grid | `experiments/EXP-Q1-FINAL-CONV/metrics.json` | BLOCKED；dt1→dt0.25 完整网格温度 36498/37800、水分 6926/37800 |
| Candidate generation | `deliverables/candidate/result1.xlsx` | NOT RUN；按阻塞规则不得生成 |
| Freeze rerun | `Q1_FREEZE_RUN` | NOT RUN；精度门未通过，不得进入双跑确认 |
| Candidate workbook validation | `scripts/validate_q1_candidate.py` | READY；候选不存在时 fail-closed |
| Human audit package | `docs/Q1_RESULT_AUDIT.md`, `docs/Q1_NUMERICAL_REMEDIATION_AUDIT.md` | READY；数值整改已完成但最终门仍等待人工审查 |

`Q1 FINAL NUMERICAL ACCURACY & DELIVERABLE GATE = BLOCKED`。不得生成 candidate 或 final `result1.xlsx`，不得启动 Q2。

## Q1 NUMERICAL CONVERGENCE DIAGNOSIS & REMEDIATION GATE

| Gate Item | Evidence | Status |
|---|---|---|
| implementation audit | `docs/Q1_NUMERICAL_REMEDIATION_AUDIT.md`；`src/q1/model.py`、`src/q1/solver.py` | PASS；中心半体积、内部几何、表面 Robin 行、BE 层级、Picard 和输出对齐均已逐项映射，未发现生产实现缺陷 |
| Level 1 raw convergence | `experiments/EXP-Q1-NUM-DIAG/metrics.json` | PASS as diagnosis；已记录 L∞/mean/RMSE、中心/表面/论文点/全网格及最大位置 |
| Level 2 order/Richardson | `experiments/EXP-Q1-NUM-DIAG/metrics.json` | PASS as diagnosis；空间温度阶约 2，BE 时间阶约 1；含水率的全网格 L∞ 受早期/表面误差主导 |
| Level 3 rounded stability | `EXP-Q1-FINAL-CONV`、`EXP-Q1-NUM-REMEDIATION` | AUXILIARY；BDF2 论文点 `0/35`，但全网格估计安全裕量未全通过 |
| error localization | `experiments/EXP-Q1-NUM-DIAG/*.svg` | PASS；已定位早期时间和表面带为含水率主要误差区域 |
| independent benchmark | `experiments/EXP-Q1-NUM-BENCH/metrics.json` | PASS；BE 空间约二阶、时间约一阶，支持生产离散的基本阶数 |
| Robin/boundary verification | `tests/test_q1_robin_boundary.py`, `pytest -q` | PASS；29 tests passed，含独立 Robin 行、中心几何和 BDF2 边界缩放测试 |
| Picard sensitivity | `experiments/EXP-Q1-PICARD-SENS/metrics.json` | PASS；非线性迭代误差远小于离散误差 |
| remediation candidate | `experiments/EXP-Q1-NUM-REMEDIATION/metrics.json` | PARTIAL；BDF2 改善论文点，但未通过全网格保守估计误差门 |
| result workbook generation | `deliverables/candidate/`, `deliverables/final/` | NOT RUN；本阶段明确禁止生成 `result1.xlsx` |
| Q2 boundary | `docs/STATE.md` | PASS；Q2–Q4 仍为 `NOT STARTED` |

`Q1 NUMERICAL REMEDIATION GATE = BLOCKED`。BDF2 仅登记为 `M1-NUM-T2` 候选；不得生成 `result1.xlsx`，不得启动 Q2。

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
