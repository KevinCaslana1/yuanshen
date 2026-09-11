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
| tests | `pytest -q` | PASS: 23 passed |
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
| candidate assumptions | `docs/ASSUMPTIONS.md`; high-impact items marked `NEEDS_REVIEW` | PASS |
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
| implementation tests | `pytest -q` | PASS: 23 passed |
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

`Q1 IMPLEMENTATION & NUMERICAL VALIDATION GATE = PASS`；当前等待人工授权进入 `Q1 RESULT & DELIVERABLE GATE`。该 Gate 不冻结最终主模型，不替代 OQ-005/OQ-006/OQ-007/OQ-008 的人工决定。

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
