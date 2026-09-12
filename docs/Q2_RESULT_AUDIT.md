# Q2 Result Audit

日期：2026-09-12（accuracy remediation 更新）

## Historical audit status before authorized V3 run

Current status: `Q2 FORMAL-OUTPUT ACCURACY GATE COMPLETE / WAITING FOR Q2 V3 FREEZE RUN AUTHORIZATION`.

This status certifies only the declared formal-output evidence chain. It does not establish a production result source and does not authorize `result2.xlsx`, Q3 or Q4.

| Gate | Result | Evidence |
|---|---|---|
| Frozen configuration recorded | PASS（历史失败候选） | `docs/Q2_PRODUCTION_FREEZE.md`, `experiments/Q2_FREEZE_RUN/config.json` |
| Fresh Run1/Run2 from `t=0` | PASS（历史失败候选） | `experiments/Q2_FREEZE_RUN/metrics.json` |
| Determinism and lineage | PASS；但不等于 accuracy PASS | `determinism.json`, `output_hashes.json`, `lineage.json` |
| Environment transition assertion | PASS as assertion；真实 discontinuity exposed | `environment.json` |
| Production field/Picard/property/residual checks | PASS（历史候选） | `run_1/metrics.json`, `diagnostics_1s.csv` |
| Original temporal/spatial accuracy confirmation | FAIL | `experiments/Q2_FREEZE_RUN/accuracy_confirmation.json` |
| Numerical remediation short/transition regression | PARTIAL；formal 1 s points pass，local first post-step probe fails | `experiments/EXP-Q2-V2-REGRESSION/metrics.json` |
| Full-horizon V2 accuracy confirmation | NOT ESTABLISHED | `experiments/Q2_FREEZE_RUN_V2/ABORTED_ATTEMPT.json` |
| Formal output scope decision | PASS；integer seconds/official radii separated from internal probes | `D-Q2-ACCURACY-SCOPE`, `accuracy_confirmation_v3.json` |
| Transition formal output lattice | PASS；T/C L∞=`1.55375452663975e-5`/`3.1402255240564614e-9` | `experiments/EXP-Q2-ACC-T-FORMAL/` |
| Early formal output lattice | PASS；T/C L∞=`7.116765686987492e-6`/`1.0270424274150258e-5` | `experiments/EXP-Q2-ACC-C-FORMAL/` |
| Targeted long-horizon certification | PASS for selected points；3–48 h uses localized n=640 reference，not full horizon | `experiments/EXP-Q2-ACC-LONG-TARGETED/` |
| Candidate workbook | NOT RUN；fail-closed | no `deliverables/candidate/result2.xlsx` |
| Q1/A题 integrity | PASS | Q1 hashes、`git diff -- A题` |
| Q3/Q4 boundary | PASS | `docs/STATE.md`, `docs/HANDOFF.md` |

## Pre-V3 reproducibility and source contract (historical)

`experiments/Q2_FREEZE_RUN/` is retained as `FAILED_PRODUCTION_ATTEMPT` and `NOT_DELIVERY_SOURCE`. Its Run1/Run2, hashes, metrics and accuracy evidence are provenance only; no formal result source is currently established. The partial `Q2_FREEZE_RUN_V2/` n=640 attempt is `ABORTED_INCOMPLETE_PERFORMANCE_REVIEW`, is not resumable, and is also not a result source. A future production attempt must use a new directory and start fresh from `t=0`.

The old Run1 raw output retains `t=0`; its official sampled region contains `228635×21=4801335` rows for times 1 through 228635 s. No V2 official workbook or formal production output has been generated. The new formal audit artifacts are validation evidence only; the result source remains unset until a separately authorized V3 production run passes determinism, lineage, sampler and workbook validation.

## Pre-V3 accuracy evidence and remediation disposition (historical)

The original full-region comparison reported temporal raw differences against `dt=.125 s` of `1.9082196854469657e-4 °C` (T) and `1.0007524800181855e-4 kg/kg` (C), and spatial raw differences against `n=160` of `5.745306611970591e-5 °C` (T) and `2.0357404664261836e-4 kg/kg` (C). These are independent fine/coarse raw differences, not Richardson uncertainties. The conservative combined envelope is the componentwise maximum (`1.9082196854469657e-4 °C`, `2.0357404664261836e-4 kg/kg`), without summing or applying optimistic extrapolation.

The accepted ENV-B convention remains unchanged: Attachment 1 is piecewise linear through `14400 s`; for `t>14400 s`, `(T_inf,C_inf)=(49.99525 °C,0.049988 kg/kg)`. The input jump is real and was not smoothed. The event-aligned BE restart reduced common integer-time transition differences in the n=80 local study. The explicit V2 n=320/cluster-power=3 regression shows a `2.2991211631051556e-4 °C` candidate/reference difference at the non-output probe `14400.25 s,r=2.0 cm`; at formal integer points in `14390..14500 s`, the maxima are T `1.55375452663975e-5 °C` and C `3.1402255240564614e-9 kg/kg`. Therefore the local first-post-step behavior is a supported bounded internal diagnostic, not a formal delivery failure.

The early moisture issue was independently recomputed as a Q2 initial compatibility check: `C0=2.55 kg/kg`, `C_inf(0)=0.01963 kg/kg`, `hm=8e-7 m/s`, `D(C0,T0)=5.641680373025664e-9 m²/s`; the discrete initial diffusion flux is `0` while the Robin flux is `2.0242959999999997e-6 kg/(m²·s)`. This is recorded only as a Q2 numerical initial-layer finding; no initial value or physical parameter was changed.

The stronger-clustering formal audit is positive on the declared scope: n=320/cluster-power=3, candidate dt=.25 s, fine startup through `5 s`, versus same-policy n=640/cluster-power=2 dt=.125 s gives early formal T/C L∞ `7.116765686987492e-6 °C`/`1.0270424274150258e-5 kg/kg`. The transition integer lattice passes while the explicit `14400.25 s,r=2.0 cm` internal temperature probe remains `2.2991211631051556e-4 °C` and bounded. The targeted long certificate gives 3–48 h T/C L∞ `1.2509725024756335e-6 °C`/`2.987415287369899e-6 kg/kg` against the localized n=640 reference; passive-neighborhood and final points pass the separate n=160 screen. This is not a full-horizon n=640 run.

## Pre-V3 candidate and figures disposition (historical)

Because no authorized V3 production run exists, `scripts/build_q2_candidate.mjs`, `scripts/validate_q2_candidate.py`, `scripts/generate_q2_figures.py`, and the Table 3/4 traceability audit remain intentionally unrun. `deliverables/candidate/result2.xlsx` does not exist; no Q2 formal figures were created. The localized audit figures/data are not production deliverables.

## Pre-V3 claims restriction (historical)

No Q2 production result may be described as an accepted deliverable before V3. The localized formal-output evidence chain does meet the predeclared gate on its declared points. The passive bracket `[207034.5,207034.75] s` is an observer used by the frozen horizon rule, not a Q3 final drying time. The internal transition dip must not be described as sudden convergence or model superiority. Current final disposition: `Q2 FORMAL-OUTPUT ACCURACY GATE COMPLETE / WAITING FOR Q2 V3 FREEZE RUN AUTHORIZATION / RESULT2 NOT GENERATED`.

## Authorized V3 freeze run and candidate gate (2026-09-12)

The latest authorization explicitly approved the V3 freeze run. The new production directory is `experiments/Q2_FREEZE_RUN_V3/`; the earlier production, V2 aborted, wrong-horizon, and post-processing-failure directories remain provenance only.

| Gate | Result | Evidence |
|---|---|---|
| Frozen V3 configuration | PASS | `Q2_FREEZE_RUN_V3/config.json`, `accuracy_basis.json` |
| Source/environment/code/Q1 integrity | PASS | `code_hashes.json`, `environment.json`, `input_hashes.json`, `preflight.json`, `validation.json` |
| Fresh Run1 and Run2 | PASS | `Q2_FREEZE_RUN_V3/metrics.json`; both fresh t=0, no restart/reuse |
| Independent passive bracket and horizon | PASS | `[206935.0,206935.25] s`; `ceil(t_high)+21600=228536 s` |
| Raw, official, diagnostic determinism | PASS | `determinism.json`, `output_hashes.json`; all byte/hash identical |
| Picard, properties, mass, heat, Robin, center, time-step residuals | PASS | `run_1/metrics.json`, `run_1/diagnostics_1s.csv`; 0 non-converged steps |
| Official sampler | PASS | `run_1/official_samples.csv`; 4,799,256 rows = 228,536×21; t=0 retained only in raw |
| Production lineage | PASS | `Q2_CANONICAL_DATA_MANIFEST.json`, `lineage.json`; Run1 only `PRODUCTION_CANONICAL` |
| Candidate result2 workbook | PASS | `candidate_validation.json`; two 228,537×22 sheets, no formulas, 4 decimals, trace 100/100 and Table3/4 60/60 |
| Formal Q2 figures | PASS | `figures/q2/FIGURE_MANIFEST.json`, `figure_validation.json`; 11 figure groups, PNG≥300 dpi + SVG, trace 30/30 |
| Q3/Q4 boundary | PASS | `STATE.md`, `HANDOFF.md`; Q3/Q4 not started |

The V3 production source is established only for the validated candidate scope. The certificate remains scoped to its declared formal-output lattice and selected long-horizon points; it is not an n=640 full-horizon proof. The `14400.25 s` transition diagnostic remains `SUPPORTED_INTERNAL_TRANSITION_DIAGNOSTIC` and is not an official integer-second output.

Current final disposition before the final freeze was `Q2 RESULT & DELIVERABLE GATE COMPLETE / WAITING FOR HUMAN Q2 FREEZE APPROVAL / RESULT2 VALIDATED CANDIDATE ONLY`.

## Q2 V3 final freeze approval (2026-09-12)

人工批准 `Q2 V3 production freeze = APPROVED` 后，执行了严格的 COPY ONLY finalization：没有重新运行 Q2、没有重新生成图表、没有重新保存或格式化 `result2.xlsx`。`deliverables/candidate/result2.xlsx` 按字节原样复制到 `deliverables/final/result2.xlsx`；现有 `figures/q2/final/` 的 11 组 PNG/SVG 按字节原样同步到 `deliverables/final/figures/q2/`。

最终只读验证结果：candidate/final `result2.xlsx` SHA-256 `84fb32457193e158debdf569d34f5f41b97e78496b30dd9b2e134385439e10da` 完全一致，大小均为 `30,303,454` bytes；两张表均为 `228537×22`，无公式，数据区数值格式为 `0.0000`；workbook trace `100/100`、Table3/4 `60/60`。最终图表为 11 组、22 个 PNG/SVG 文件，PNG DPI 不低于 300，图表 trace `30/30`。全仓测试为 `56 passed`。

冻结记录：`experiments/Q2_FINAL_FREEZE/freeze_record.json`；最终清单：`deliverables/final/Q2_MANIFEST.json`。Run1/Run2 均独立从 `t=0` 运行且 raw/sampled/diagnostics byte/hash 一致；passive interval 为 `[206935.0,206935.25] s`，final horizon 为 `228536 s`。历史失败实验 `Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912` 仍保留为审计记录，未进入 final 交付。

当前最终状态：`Q2 = FROZEN`。Q1 仍保持 `pointwise error zero-crossing / cancellation dip` 的深谷解释；Q3/Q4 仍为 `NOT STARTED`。
