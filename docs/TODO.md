# TODO

状态：`TODO` / `DOING` / `BLOCKED` / `DONE` / `CANCELLED`  
优先级：`P0` 必须完成，`P1` 重要，`P2` 可选优化，`P3` 有时间再做。

每项任务只有在 `Acceptance Criteria` 全部满足后才能标记 `DONE`。

| Task ID | Priority | Question | Depends | Status | Expected Artifact | Acceptance Criteria | Timebox |
|---|---|---|---|---|---|---|---|
| T-001 | P0 | 全局 | — | DONE | `docs/PROBLEM_SPEC.md` | A题事实、Q1-Q4、输入输出和未决项均已分层登记，未写建模方案 | 本轮 |
| T-002 | P0 | 全局 | T-001 | DONE | `docs/DATA_CATALOG.md` | 7 个官方资产均有路径、类型、大小、SHA-256、结构与保护状态 | 本轮 |
| T-003 | P0 | 全局 | T-001 | DONE | `AGENTS.md`, `problem/README.md` | `A题/` 被声明为不可写官方源，禁止复制出第二个原始数据源 | 本轮 |
| T-004 | P0 | Q1-Q4 | T-002 | DONE | `src/q4/`, `docs/STATE.md`, `docs/VALIDATION.md` | Q1、Q2、Q3、Q4 均已注册，模板不再只支持 Q1-Q3 | 本轮 |
| T-005 | P0 | 全局 | T-002 | DONE | `scripts/validate_inputs.py`, `scripts/validate_templates.py` | 输入存在性、哈希、Sheet、行列骨架和模板空白完整性检查可执行 | 本轮 |
| T-006 | P1 | 全局 | T-005 | DONE | `deliverables/README.md` | 官方模板到 candidate、验证、人工确认、final 的隔离流程已建立 | 本轮 |
| T-007 | P1 | 全局 | T-001 | DONE | `requirements.txt`, `requirements-dev.txt`, `docs/RUNBOOK.md` | Python 兼容范围、pip、openpyxl、pytest、安装和验证命令已记录；当前 `.venv` 可运行 | 1 个会话 |
| T-008 | P1 | 全局 | T-001 | DONE | 人工审查前置条件 | 仓库、官方资产、题目事实和当前状态无新不一致 | 15 分钟 |
| T-009 | P0 | 全局 | T-007 | DONE | `.venv` | 独立环境安装 requirements 成功，版本可读 | 本轮 |
| T-010 | P0 | 全局 | T-002 | DONE | `docs/DELIVERABLE_SPEC.md`, `config/deliverables.json` | result1-result4 的模板、路径、单位、采样、精度、骨架/最终形状状态已登记 | 本轮 |
| T-011 | P0 | 全局 | T-010 | DONE | `scripts/validate_deliverable_contract.py` | JSON 与 Markdown 契约、路径、Sheet、单位、精度、Open Question 状态检查通过 | 本轮 |
| T-012 | P0 | 全局 | T-011 | DONE | `tests/` | 12 个 Workflow 测试通过；不包含模型测试 | 本轮 |
| T-013 | P0 | 全局 | T-012 | DONE | `docs/VALIDATION.md` | Pre-Modeling Gate 所有必要项已审计并标记 PASS | 本轮 |
| T-014 | P0 | Q1 | T-013 | DONE | `docs/Q1_PLAN.md` | Q1 Requirement Matrix 已回到官方 PDF、附件1和 result1 模板核对，并区分事实/解释/建模选择 | 本轮 |
| T-015 | P0 | Q1 | T-014 | DONE | `docs/Q1_PLAN.md` | 附件1数据类型、时间范围、间隔、缺失、重复、范围和未修改状态完成审计 | 本轮 |
| T-016 | P0 | Q1 | T-014 | DONE | `docs/Q1_PLAN.md` | Q1变量、原始/内部/输出单位和转换规则登记完成 | 本轮 |
| T-017 | P0 | Q1 | T-016 | DONE | `docs/ASSUMPTIONS.md` | Q1正式候选假设已登记，高影响假设标记 `NEEDS_REVIEW` | 本轮 |
| T-018 | P0 | Q1 | T-017 | DONE | `docs/Q1_PLAN.md` | Baseline、Main Candidate、Alternative Candidates 已比较并记录限制 | 本轮 |
| T-019 | P0 | Q1 | T-018 | DONE | `docs/Q1_PLAN.md` | Baseline 设计、主候选方程和推荐进入实现的条件已登记 | 本轮 |
| T-020 | P0 | Q1 | T-019 | DONE | `docs/Q1_PLAN.md` | 空间离散、时间离散、边界、插值、稳定性和收敛策略已设计 | 本轮 |
| T-021 | P0 | Q1 | T-020 | DONE | `docs/Q1_PLAN.md` | Q1 Validation Plan 已覆盖适用的初值、单位、边界、范围、连续性、敏感性、收敛和 Baseline 检查 | 本轮 |
| T-022 | P0 | Q1 | T-021 | DONE | `docs/EXPERIMENTS.md`, `experiments/EXP-001/`–`EXP-007/` | EXP-001 至 EXP-007 按序完成；配置、指标、命令、代码提交和输入哈希可追溯；无最终结果产物 | 本轮 |
| T-023 | P0 | Q1 | T-022 | DONE | `docs/Q1_PLAN.md`, `docs/DECISIONS.md` | Q1 Model Design Review 完成；实现候选仍等待 Result Gate 冻结 | 本轮 |
| T-024 | P0 | Q1 | T-023 | DONE | `src/q1/`, `src/common/numerics.py`, `tests/test_q1_numerics.py` | M1、M2、B0、M3 可重复运行；中心、Robin、通量、单位、路径保护和确定性测试通过 | 本轮 |
| T-025 | P0 | Q1 | T-024 | DONE | `docs/VALIDATION.md`, `experiments/EXP-001/`–`EXP-007/` | 烟雾、时间/空间敏感性、边界/插值敏感性、Baseline 和守恒/范围检查均有证据 | 本轮 |
| T-026 | P0 | Q1 | T-025 | DONE | `Q1 FULL-HORIZON PRODUCTION CONFIG FREEZE & CANDIDATE DELIVERABLE GATE` | OQ-005/006/007/008 已解决；完整输出网格按团队离散不确定度标准通过，舍入仅作辅助 | 本轮 |
| T-027 | P0 | Q1 | T-026 | DONE | `docs/Q1_NUMERICAL_REMEDIATION_AUDIT.md`、`experiments/EXP-Q1-NUM-*` | 实现审计、独立 benchmark、误差定位、Picard、BDF2、聚簇网格和全时域收敛证据已完成 | 本轮 |
| T-028 | P0 | Q1 | T-027 | DONE | 局部数值整改决策与复验 | 已按人工授权完成初始层兼容性、表面误差衰减、BDF2 启动和边界聚类 benchmark/短时复验；无工作簿写入 | `docs/Q1_INITIAL_LAYER_AUDIT.md`、EXP-Q1-INITIAL-LAYER 至 EXP-Q1-CLUSTER-TEMPORAL |
| T-029 | P0 | Q1 | T-028 | DONE | 聚类候选 0–1800 s 全网格复验 | 固定候选网格/时间策略后，raw、Richardson、守恒/范围、初始层和全网格舍入辅助认证完成；官方资产只读 | 本轮 |
| T-030 | P0 | Q1 | T-029 | DONE | Q1 RESULT & DELIVERABLE GATE | 全时域温度/含水率估计不确定度均 `<5e-5`，生产配置冻结并完成候选验证 | 本轮 |
| T-031 | P0 | Q1 | T-030 | DONE | Human Q1 freeze approval and final handoff | 人工批准已登记；candidate 已 COPY ONLY 到 `deliverables/final/`，final 工作簿/清单、最终校验、图表包和审计记录均完成；不得自动进入 Q2 | 2026-09-11 |
| T-032 | P0 | Q2 | T-031 | DONE | `docs/Q2_PLAN.md`、Q2 实验审计与相关登记文档 | 官方要求、附录3、delta matrix、团队资料 reconciliation、模型/数值候选、验证和交付契约草案全部完成；不实现 solver | 本轮 |
| T-037 | P0 | Q1 | T-031 | DONE | `experiments/EXP-Q1-SURFACE-DECAY/`、`experiments/EXP-003/`、`experiments/EXP-004/` | signed/absolute 原始误差、15–45 s 表、signed 图、absolute semilogy 图、0–60 s 边界/求解轨迹、固定 dt/dr 的全时域 L∞/L2/observed order 和谷值移动检查完成；不修改 final result1.xlsx | 2026-09-11 |
| T-033 | P0 | Q2 | T-032 | DONE | Human authorization for Q2 implementation | 已收到人工批准，范围仅含 Q2 implementation、短时验证和0–3 h内部验证；不含 final `result2.xlsx`、Q3/Q4 | 2026-09-11 |
| T-034 | P1 | Q2 | T-032 | DONE | Decide post-14400 s environment | 已批准 `t>14400 s` 常值 `T_inf=49.99525 °C`、`C_inf=0.049988 kg/kg`，并记录切换跳变 | 2026-09-12 |
| T-035 | P1 | Q2 | T-032 | DONE | Decide variable-coefficient interface mean | 已批准 production 使用 harmonic；arithmetic 仅保留 sensitivity | 2026-09-12 |
| T-036 | P1 | Q2 | T-032 | DONE | Decide Q2 end/accuracy contract | 已批准 passive bracket+safety tail horizon 和内部 `2.5e-5` gate；不把 Q3 threshold 当 Q2 endpoint | 2026-09-12 |
| T-038 | P0 | Q2 | T-033 | DONE | Q2 implementation & short-horizon validation | `src/q2/`、属性/环境/变量系数 FVM、coupled Picard、EXP-Q2-001 至 EXP-Q2-011、测试、checkpoint/restart 和0–3 h内部验证完成；无 `result2.xlsx` | 2026-09-11 |
| T-039 | P1 | Q2 | T-038 | DONE | Human review of Q2 open decisions | 最新人工批准已转入 production freeze；实际值记录于 `docs/Q2_PRODUCTION_FREEZE.md` | 2026-09-12 |
| T-040 | P0 | Q2 | T-039 | DONE | Q2 long-horizon boundary & production config gate | `EXP-Q2-012`–`EXP-Q2-020` 完成环境尾段/插值/边界/界面平均/0–72 h、被动事件、低含水率物性、守恒/Robin、重启、长时收敛和 B0 对照；raw/recovered 证据完整；未生成 `result2.xlsx` | 2026-09-11 |
| T-041 | P0 | Q2 | T-040 | DONE | Freeze Q2 production configuration | 配置已冻结并执行双跑；环境跳变与内部精度门均显式记录 | 2026-09-12 |
| T-042 | P0 | Q2 | T-041 | BLOCKED | Generate and validate Q2 candidate deliverable | accuracy confirmation FAIL；只有整改后重新取得 PASS 才能从官方模板生成 candidate | `docs/Q2_RESULT_AUDIT.md` |
| T-043 | P0 | Q3/Q4 | T-042 | TODO | Start Q3/Q4 only after explicit authorization | Q3/Q4 当前保持 NOT STARTED，不因 Q2 被动事件观察 bracket 自动启动 | 待确认 |

| T-044 | P0 | Q2 human model-decision packet | T-040 | DONE | `docs/Q2_HUMAN_DECISION_PACKET.md`、`experiments/Q2_CANONICAL_DATA_MANIFEST.json` | D1–D7 证据、定向关键数据、recommendation、risk 和人工审批表完整；无 result2；Q1/Q3/Q4边界保持 | 2026-09-11 |
| T-045 | P0 | Human approval of Q2 production decisions | T-044 | DONE | D-Q2-ENVIRONMENT 等七项 | latest authorization approved production freeze decisions；不豁免 accuracy gate | 2026-09-12 |
| T-046 | P0 | Q2 production candidate and result2 validation | T-045 | BLOCKED | `deliverables/candidate/result2.xlsx` | production accuracy gate FAIL；candidate 不得生成，Q3/Q4 不得启动 | `experiments/Q2_FREEZE_RUN/accuracy_confirmation.json` |
| T-047 | P1 | Start Q3/Q4 after explicit authorization | T-045 | TODO | Q3/Q4 实验与计划 | Q3/Q4 仍 NOT STARTED；不得把 Q2 passive bracket 当作 Q3 answer | 待确认 |
| T-048 | P0 | Q2 accuracy remediation decision and rerun | T-046 | DONE | `accuracy_confirmation_v3.json`、formal transition/early/targeted long experiments | `D-Q2-ACCURACY-SCOPE` 已登记；formal output gate 完成；内部 `14400.25 s` probe 有界且未传播 | 2026-09-12 |
| T-049 | P0 | Q2 V3 freeze-run accuracy and deliverable validation | T-048 | TODO | 新 attempt 目录中的 fresh Run1/Run2、determinism、lineage、candidate workbook、Q2 figures | 仅在人工授权后执行；推荐 n320/cluster3 + early through5 s；不得续跑 `Q2_FREEZE_RUN_V2` | 待人工授权 |

## 任务记录模板

```text
T-xxx
Task ID:
Priority: P0/P1/P2/P3
Question: Q1/Q2/Q3/Q4/全局
Depends: T-xxx 或 —
Status: TODO/DOING/BLOCKED/DONE/CANCELLED
Expected Artifact:
Acceptance Criteria:
Timebox:
备注：
```

只新增会影响未来工作的任务；优先完成 P0/P1，不自行堆积大量 P2/P3。
