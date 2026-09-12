# Q2 Production Freeze

日期：2026-09-12
授权：`Q2 HUMAN PRODUCTION FREEZE APPROVAL = APPROVED`

## 状态

历史配置冻结和双跑仍保留为失败 provenance；本轮已依据人工 `Q2 V3 FREEZE RUN AUTHORIZATION = APPROVED` 完成 V3 生产、候选工作簿和正式图表门禁。Q2 当前状态为 `VALIDATED CANDIDATE / WAITING FOR HUMAN Q2 FREEZE APPROVAL`；candidate 尚未进入 `deliverables/final/`，Q1 保持 FROZEN，Q3/Q4 保持 NOT STARTED。

## Frozen model and configuration

### Physics and units

- Fixed 1D cylindrical radial domain: `R=0.02 m`, `L=0.25 m`.
- Internal units: `s`, `m`, `°C`/`K`, `kg/kg`, `kg/m³`, `J/(kg·K)`, `W/(m·K)`, `W/(m²·K)`, `m/s`, `m²/s`.
- Appendix 3 properties: `rho=650+128C kg/m³`; `cp=1450+2736C/(C+1) J/(kg·K)`; `k=0.21+0.38C/(C+1) W/(m·K)`; `D=2.4e-3 exp(-0.45/C) exp(-3850/T_K) m²/s`.
- Center symmetry and Robin heat/moisture boundaries; coupled temperature–moisture Picard. Latent heat, shrinkage, moving boundary and other Q4 physics are not included.

### Boundary environment

- Source: `A题/附件/附件1.xlsx`, SHA-256 `7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7`.
- `0..14400 s`: raw Attachment 1, piecewise linear interpolation.
- `t>14400 s`: constant `T_inf=49.99525 °C`, `C_inf=0.049988 kg/kg`, with no smoothing.
- The explicit transition audit records raw `(50.165, 0.04986)` at `14400 s` and constant `(49.99525, 0.049988)` immediately after it; the resulting jump is `(-0.16975 °C,+0.000128 kg/kg)`.
- `h=25 W/(m²·K)` and `hm=8e-7 m/s` are carried-forward modeling assumptions, not official Q2 parameters.

### Historical original numerical production candidate (not delivery source)

- Candidate A: boundary-clustered conservative FVM, `cluster_power=2`.
- Requested `n_intervals=80`; actual `98` cells and `99` nodes; `min dr=3.124999999999656e-6 m`, `max dr=4.968749999999988e-4 m`.
- `dt=0.25 s`; first step Backward Euler; subsequent steps BDF2; harmonic interface mean.
- Picard tolerance `1e-8`, maximum 50 iterations, relaxation 1.0; output interval 1 s.
- Passive event is an observer only: `g=max(C)-0.15`; first directional bracket `[207034.5,207034.75] s`; `final_horizon=228635 s` after the 21600 s safety tail. This is not a Q3 drying time.

## Production lineage and integrity

- Baseline commit: `828f27a96d2f2ed93184b30cc2379136553f73b5`.
- Formal source: `NONE`；`experiments/Q2_FREEZE_RUN/run_1/official_samples.csv` is retained only as `FAILED_PRODUCTION_ATTEMPT` provenance.
- Run1/run2 raw SHA-256: `48584714d347aed619d56b564f737668cc418d63067daca49b0bceaf75bd548c`.
- Run1/run2 sampled SHA-256: `604a323955c2ab5cd1299975231997b3dc6e5c0c6a2e16d6e52d6314a6050eae`.
- Run1/run2 diagnostics SHA-256: `219f7a38f130f11ad8c896278f2fc4ce4bc881196b7f0a7f2a133d9af14819b5`.
- Run1/run2 checkpoint SHA-256: `7a19676261efc9c2f96d4a8c34b6302a14a63d5cf84bcf408b90f623c6cbf104`.
- `A题/` is unchanged; Q1 final SHA-256 remains `06b67b1f688d84a701ac4d2f4b0f47a1624069877df6724faf071a48af177b5c`.

## Historical original gate result

The full official output region is `t=1..228635 s` and 21 radii. The independent references use the same inputs/code with `dt=0.125 s`, `dt=0.5 s`, and `n_intervals=160`, each from fresh `t=0` starts. The internal uncertainty gate is `2.5e-5` for both fields; it is not an official requirement, but it was explicitly frozen as a fail-closed production gate.

| Metric | Estimate | Gate | Status |
|---|---:|---:|---|
| Temperature L∞ | `1.9082196854469657e-4 °C` | `2.5e-5 °C` | FAIL |
| Temperature L2 RMS | `4.400124076121024e-6 °C` | `2.5e-5 °C` | PASS |
| Moisture L∞ | `2.0357404664261836e-4 kg/kg` | `2.5e-5 kg/kg` | FAIL |
| Moisture L2 RMS | `3.0182278875418313e-5 kg/kg` | `2.5e-5 kg/kg` | FAIL |

The time observed order from the frozen `dt=.5/.25/.125` comparison is `1.6685` for temperature and `3.0631` for moisture under the global L∞ metric; it is not sufficient to claim uniform first-order behavior for this production configuration.

## Formal-output certificate disposition before V3 (historical)

The formal-output candidate gate is complete on its declared points. Recommended `Q2_NUMERICAL_CONFIG_V3`: n=320/cluster_power=3, fine `dt=.015625 s` through5 s, production `dt=.25 s`, BE startup/BDF2, BE restart at the exact environment transition and step-policy change, harmonic interfaces, ENV-B. Transition formal T/C L∞ are `1.55375452663975e-5 °C`/`3.1402255240564614e-9 kg/kg`; early formal T/C L∞ are `7.116765686987492e-6 °C`/`1.0270424274150258e-5 kg/kg`. The targeted long certificate passes 3–48 h with a localized n=640 reference and covers passive/final points with the recorded moderate screen.

The n=320 candidate's explicit non-output probe `14400.25 s,r=2.0 cm` remains `2.2991211631051556e-4 °C`; it is a bounded internal diagnostic and does not propagate to formal output points. The attempted n=640 V2 full run remains incomplete provenance and is not resumed. Do not generate `result2.xlsx` before V3 authorization, do not call the passive bracket a Q3 drying time, and do not start Q3/Q4.

Evidence: `experiments/Q2_FREEZE_RUN/metrics.json`, `environment.json`, `determinism.json`, `accuracy_confirmation.json`, `accuracy_diagnosis.json`, `experiments/Q2_ACCURACY_REMEDIATION/accuracy_confirmation_v3.json`, `experiments/EXP-Q2-ACC-T-FORMAL/`, `experiments/EXP-Q2-ACC-C-FORMAL/`, `experiments/EXP-Q2-ACC-LONG-TARGETED/`, `experiments/EXP-Q2-V2-REGRESSION/`, and `experiments/Q2_FREEZE_RUN_V2/ABORTED_ATTEMPT.json`.

## V3 production run and candidate disposition (2026-09-12)

The authorized V3 run uses the frozen `Q2_NUMERICAL_CONFIG_V3` exactly: n=320/cluster3, harmonic interfaces, fine `dt=.015625 s` through 5 s, production `dt=.25 s`, BE startup/BDF2, BE restart at the 5 s step-policy transition and exact 14400 s environment transition, linear Attachment 1 input followed by constant ENV-B. Both runs started fresh at t=0 and independently derived the same passive bracket `[206935.0,206935.25] s`; therefore `final_horizon=228536 s`.

Run 1 is the sole production source and Run 2 is a determinism reference. Raw internal output retains t=0; official output is the integer-second lattice t=1..228536 at 21 radii. Raw, official sampled, and 1 s diagnostics are byte/hash identical between runs. Run 1 diagnostics report 0 non-converged steps, Picard iterations 2–3, mass residual max `1.543877133753609e-8`, heat residual max `1.2148866494281616 J`, heat Robin residual max `1.252318826748482e-4 W/m²`, and moisture Robin residual max `4.541557986191563e-12 kg/(m²·s)`.

The formal accuracy basis remains scoped to the declared integer-second/official-radius points and selected long-horizon points; it is not a full-horizon n=640 proof. The internal transition peak at 14400.25 s remains `SUPPORTED_INTERNAL_TRANSITION_DIAGNOSTIC` and is not an official output point.

`deliverables/candidate/result2.xlsx` was generated from the canonical Run 1 source with a write-only streaming fallback after artifact-tool heap failures. The two sheets pass shape, 4-decimal, no-formula, 100/100 random trace, and Table 3/4 60/60 trace checks. Eleven Q2 figure groups pass PNG ≥300 dpi + SVG, source-hash, no-smoothing/no-interpolation, and 30/30 trace checks. The workbook is a `VALIDATED CANDIDATE` only; it must not be copied into `deliverables/final/` until human Q2 freeze approval.

Evidence: `experiments/Q2_FREEZE_RUN_V3/`, `experiments/Q2_CANONICAL_DATA_MANIFEST.json`, `experiments/Q2_FREEZE_RUN_V3/candidate_validation.json`, `experiments/Q2_FREEZE_RUN_V3/figure_validation.json`, `figures/q2/FIGURE_MANIFEST.json`.
