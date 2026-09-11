# Q2 Result Audit

日期：2026-09-12

## Audit status

| Gate | Result | Evidence |
|---|---|---|
| Frozen configuration recorded | PASS | `docs/Q2_PRODUCTION_FREEZE.md`, `experiments/Q2_FREEZE_RUN/config.json` |
| Fresh Run1/Run2 from `t=0` | PASS | `experiments/Q2_FREEZE_RUN/metrics.json` |
| Determinism and lineage | PASS | `determinism.json`, `output_hashes.json`, `lineage.json` |
| Environment transition assertion | PASS as assertion; discontinuity exposed | `environment.json` |
| Production field/Picard/property/residual checks | PASS | `run_1/metrics.json`, `diagnostics_1s.csv` |
| Temporal/spatial accuracy confirmation | FAIL | `accuracy_confirmation.json` |
| Candidate workbook | NOT RUN; fail-closed | `validation.json` |
| Q1/A题 integrity | PASS | `metrics.json`, `git diff -- A题` |
| Q3/Q4 boundary | PASS | `docs/STATE.md`, `docs/HANDOFF.md` |

## Reproducibility contract

The only formal production result source is `experiments/Q2_FREEZE_RUN/run_1`. Run2 is a fresh deterministic reference. Old validation, recovered, interrupted or duplicate files are not formal sources. The raw output retains `t=0`; the official sampled region removes exactly 21 `t=0` rows and contains `228635×21=4801335` rows for times 1 through 228635 s.

## Accuracy evidence

The comparison covered every official second and every official radius. The largest temperature difference against `dt=.125 s` is `1.9082196854469657e-4 °C` at `14401 s, 2.0 cm`; the largest moisture difference against `n=160` is `2.0357404664261836e-4 kg/kg` at `1 s, 2.0 cm`. The corresponding by-time CSVs retain all pointwise errors and were generated without smoothing or interpolation.

The failure is independently reproducible. Attachment 1 gives `(50.165,0.04986)` at `14400 s`; the approved post-attachment constants give `(49.99525,0.049988)` immediately after the knot. The discontinuity explains the temporal peak at 14401 s. The spatial peak at 1 s is an initial-layer resolution effect at the surface. This evidence does not prove a solver assembly bug, but it does prove that the frozen candidate fails the explicitly frozen internal uncertainty gate.

## Candidate and figures disposition

Because the accuracy status is `FAIL`, `scripts/build_q2_candidate.mjs`, `scripts/validate_q2_candidate.py`, `scripts/generate_q2_figures.py`, and the Table 3/4 traceability audit were intentionally not run. `deliverables/candidate/result2.xlsx` does not exist; no Q2 production figures were created. This is an audit stop, not a successful result gate.

## Claims restriction

No Q2 result may be described as meeting the internal accuracy gate. The passive bracket `[207034.5,207034.75] s` is an observer used by the frozen horizon rule, not a Q3 final drying time. No statement about sudden convergence, model superiority, or official acceptance is supported by this run.
