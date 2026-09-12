# Q2 Result Audit

日期：2026-09-12（accuracy remediation 更新）

## Audit status

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
| Candidate workbook | NOT RUN；fail-closed | no `deliverables/candidate/result2.xlsx` |
| Q1/A题 integrity | PASS | Q1 hashes、`git diff -- A题` |
| Q3/Q4 boundary | PASS | `docs/STATE.md`, `docs/HANDOFF.md` |

## Reproducibility and source contract

`experiments/Q2_FREEZE_RUN/` is retained as `FAILED_PRODUCTION_ATTEMPT` and `NOT_DELIVERY_SOURCE`. Its Run1/Run2, hashes, metrics and accuracy evidence are provenance only; no formal result source is currently established. The partial `Q2_FREEZE_RUN_V2/` n=640 attempt is `ABORTED_INCOMPLETE_PERFORMANCE_REVIEW`, is not resumable, and is also not a result source. A future production attempt must use a new directory and start fresh from `t=0`.

The old Run1 raw output retains `t=0`; its official sampled region contains `228635×21=4801335` rows for times 1 through 228635 s. No V2 official workbook or formal production output has been generated.

## Accuracy evidence and remediation disposition

The original full-region comparison reported temporal raw differences against `dt=.125 s` of `1.9082196854469657e-4 °C` (T) and `1.0007524800181855e-4 kg/kg` (C), and spatial raw differences against `n=160` of `5.745306611970591e-5 °C` (T) and `2.0357404664261836e-4 kg/kg` (C). These are independent fine/coarse raw differences, not Richardson uncertainties. The conservative combined envelope is the componentwise maximum (`1.9082196854469657e-4 °C`, `2.0357404664261836e-4 kg/kg`), without summing or applying optimistic extrapolation.

The accepted ENV-B convention remains unchanged: Attachment 1 is piecewise linear through `14400 s`; for `t>14400 s`, `(T_inf,C_inf)=(49.99525 °C,0.049988 kg/kg)`. The input jump is real and was not smoothed. The event-aligned BE restart reduced common integer-time transition differences in the n=80 local study, but the explicit V2 n=320/cluster-power=3 regression shows a `2.2991211631051556e-4 °C` candidate/reference difference at the non-output probe `14400.25 s,r=2.0 cm`; at formal integer points in `14390..14500 s`, the maximum is `1.55375452663975e-5 °C`. Therefore the local first-post-step behavior is not certified, and it must not be described as a complete V2 accuracy pass.

The early moisture issue was independently recomputed as a Q2 initial compatibility check: `C0=2.55 kg/kg`, `C_inf(0)=0.01963 kg/kg`, `hm=8e-7 m/s`, `D(C0,T0)=5.641680373025664e-9 m²/s`; the discrete initial diffusion flux is `0` while the Robin flux is `2.0242959999999997e-6 kg/(m²·s)`. This is recorded only as a Q2 numerical initial-layer finding; no initial value or physical parameter was changed.

The stronger-clustering short study is positive but limited: n=320/cluster-power=3 versus n=640/cluster-power=2 at fixed `dt=.015625 s` through `2 s` gives moisture L∞ `2.5626144490864533e-6 kg/kg` and temperature L∞ `1.0052019661088707e-8 °C`. The 0–3 h plus transition regression completed for the candidate and dt=.125 reference, but the local probe result above and the absence of a complete full-horizon V2 run keep the gate blocked.

## Candidate and figures disposition

Because no V2 full-horizon accuracy confirmation exists, `scripts/build_q2_candidate.mjs`, `scripts/validate_q2_candidate.py`, `scripts/generate_q2_figures.py`, and the Table 3/4 traceability audit remain intentionally unrun. `deliverables/candidate/result2.xlsx` does not exist; no Q2 formal figures were created.

## Claims restriction

No Q2 result may be described as meeting the internal accuracy gate. The passive bracket `[207034.5,207034.75] s` is an observer used by the frozen horizon rule, not a Q3 final drying time. No statement about sudden convergence, model superiority, or official acceptance is supported. Current final disposition: `Q2 NUMERICAL ACCURACY REMEDIATION GATE BLOCKED / DO NOT GENERATE RESULT2 / WAITING FOR HUMAN REVIEW`.
