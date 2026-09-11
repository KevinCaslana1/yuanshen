# Q2 HUMAN MODEL-DECISION FREEZE PACKET

状态：`Q2 HUMAN MODEL-DECISION PACKET COMPLETE / WAITING FOR HUMAN Q2 PRODUCTION FREEZE APPROVAL`

本文件只登记人工冻结所需的证据、推荐和风险。所有推荐的状态均为
`RECOMMENDED_FOR_HUMAN_APPROVAL`，没有任何一项被写成 `FINAL` 或
`APPROVED`。本轮没有生成 `result2.xlsx`、candidate/final workbook，也没有启动
Q3/Q4；Q1 保持冻结。

## D1 Environment after 14400 s

### Official facts

- 官方附件1给出环境输入至 `14400 s`；题面没有给出 `14400 s` 之后的唯一延拓规则。
- 因此，后续恒值环境是团队建模决策，不是官方 Q2 参数事实。
- `T_inf` 的单位为 `°C`，`C_inf` 的单位为 `kg/kg`；内部计算显式转换为 `K` 和 `kg/kg`。

### Team-reference proposals

- `ENV-A-last-raw`：取附件1最后原始点，`T_inf=50.165 °C`、`C_inf=0.04986 kg/kg`，之后保持常值。
- `ENV-B-tail40-mean`：取最后40个原始点 `12060–14400 s` 的均值，`T_inf=49.99525 °C`、`C_inf=0.049988 kg/kg`，之后保持常值。
- `TEAM-REFERENCE`：`50.0 °C / 0.0500 kg/kg`，仅为团队参考，不是官方数据。

### Tail evidence

数据来源：`experiments/EXP-Q2-012-ENVIRONMENT/metrics.json`。`std` 是总体标准差，斜率是对真实时间窗口的线性回归斜率；没有先四舍五入。

| window | real time range (s) | T_inf mean (°C) | T_inf std (°C) | T tail slope (°C/s) | C_inf mean (kg/kg) | C_inf std | C tail slope ((kg/kg)/s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| last point | 14400 | 50.165 | N/A | N/A | 0.04986 | N/A | N/A |
| tail10 | 13860–14400 | 50.0465 | 0.15827649857132883 | -3.0191919191919093e-4 | 0.049928 | 8.518215775618748e-5 | 2.34343434343436e-7 |
| tail20 | 13260–14400 | 50.01765 | 0.16031321685999594 | -1.981203007518872e-5 | 0.0499795 | 1.1710999103407022e-4 | -1.3270676691729406e-7 |
| tail40 | 12060–14400 | 49.99525 | 0.1558534167094195 | 3.0009380863039627e-5 | 0.049988 | 1.3746272221951646e-4 | -2.91432145090673e-8 |
| tail60 | 10860–14400 | 49.995666666666665 | 0.15222873870885523 | 6.3628785773826524e-6 | 0.04999116666666667 | 1.4743463711835888e-4 | -9.905529313697712e-9 |
| tail80 | 9660–14400 | 50.004125 | 0.15521536449398313 | -3.5681356461948846e-6 | 0.049995375 | 1.561325058243798e-4 | -1.0026957337083542e-8 |

Tail40–80 have small fitted slopes relative to their standard deviations, but the
single last point is not close to their mean in temperature. This is a tail-noise
versus endpoint-continuity decision, not evidence that the tail is exactly constant.

### ENV-A versus ENV-B long-horizon impact

Both runs use the same `n=80`, `dt=0.25 s`, BDF2, linear interpolation, harmonic
face mean and fixed geometry. Values below are computed from the checkpoint fields;
`mean C` is the arithmetic mean over the 81 solver nodes and `max C` is the nodal
maximum. Source: `experiments/EXP-Q2-018-ENV-COMPARISON/metrics.json` plus exact
checkpoint reduction.

| time | center T A/B (°C) | surface T A/B (°C) | center C A/B | surface C A/B | max C A/B | mean C A/B |
|---:|---:|---:|---:|---:|---:|---:|
| 6 h | 50.1645194811 / 49.9952444708 | 50.1647329990 / 49.9952469278 | 1.0155593633 / 1.0170085291 | 0.5334481529 / 0.5327550579 | 1.0155593633 / 1.0170085291 | 0.7831848220 / 0.7836496726 |
| 24 h | 50.1650000000 / 49.9952500000 | 50.1650000000 / 49.9952500000 | 0.2371287602 / 0.2378442077 | 0.0662637446 / 0.0664577367 | 0.2371287602 / 0.2378442077 | 0.1811014113 / 0.1815805699 |
| 48 h | 50.1650000000 / 49.9952500000 | 50.1650000000 / 49.9952500000 | 0.1614912913 / 0.1618676003 | 0.0535821010 / 0.0537245556 | 0.1614912913 / 0.1618676003 | 0.1294339418 / 0.1297012883 |
| 72 h | 50.1650000000 / 49.9952500000 | 50.1650000000 / 49.9952500000 | 0.1374341286 / 0.1377116974 | 0.0516273255 / 0.0517616153 | 0.1374341286 / 0.1377116974 | 0.1123660160 / 0.1125694525 |

Global field differences (`A-B`) are non-negligible: temperature L∞ is
`0.1694860712/0.1697500000/0.1697500000/0.1697500000 °C` at 6/24/48/72 h;
moisture L∞ is `0.0014491658/0.0007154475/0.0003763091/0.0002775688 kg/kg`.
The passive observer bracket is `205913–205913.25 s` for A and
`207034.5–207034.75 s` for B, a shift of `+1121.5 s`; this is a passive diagnostic,
not a Q3 drying time.

### 14400 s transition audit

At `14400 s`, the attachment value is `50.165 °C / 0.04986 kg/kg`.

| candidate | first post-attachment constant | ΔT | ΔC | instantaneous heat Robin flux jump (W/m²) | instantaneous mass Robin flux jump (kg/(m²·s)) |
|---|---|---:|---:|---:|---:|
| ENV-A | 50.165 / 0.04986 | 0 | 0 | 0 | 0 |
| ENV-B | 49.99525 / 0.049988 | -0.1697500000000005 | 0.00012799999999999617 | -4.243750000000013 | 1.0239999999999693e-10 |
| TEAM-REFERENCE | 50.0 / 0.05 | -0.16499999999999915 | 0.00014000000000000123 | -4.124999999999979 | 1.1200000000000098e-10 |

No transition smoothing is applied. A produces continuity by construction. B and the
team reference introduce a defined stage-switch jump; the B heat-flux jump is large
enough that it cannot be treated as a negligible numerical perturbation.

### Recommendation and human decision

- **Recommendation:** `ENV-A-last-raw`, because it preserves the measured endpoint,
  is continuous at `14400 s`, is deterministic and easiest to reproduce. Keep
  tail40 as an explicit alternative if the team chooses measurement-noise robustness
  over endpoint continuity; do not silently replace A with B.
- **Risk if chosen:** the last raw endpoint may be an outlier relative to the tail
  mean, producing a warm long-horizon environment and sensitivity in the moisture field.
- **Risk if rejected:** choosing tail40 without a declared transition rule creates a
  discontinuity and changes the long field materially; choosing `50/0.05` would not be
  traceable to the official attachment.
- **Required human decision:** choose A, B, or request another declared post-attachment
  rule. Status: `D-Q2-ENVIRONMENT = RECOMMENDED_FOR_HUMAN_APPROVAL`.

## D2 Linear vs PCHIP

### Official facts

The attachment knots are official input values. The interpolation between knots is
not fixed by the problem statement. Both implementations reproduce the raw knots
exactly; PCHIP is an additional smooth interpolation assumption.

### Team-reference proposal

Use piecewise linear interpolation for transparency and auditability, subject to the
comparison below and human approval. This is a recommendation from evidence, not an
automatic carry-over from Q1.

### Experimental evidence and quantitative impact

Source: `experiments/EXP-Q2-013-INTERPOLATION/`. The table compares linear and PCHIP
at the exact Table 3/Table 4 radii `0, 0.5, 1, 1.5, 2 cm`; the value is the maximum
absolute difference across those five radii at that paper time, using full-precision
CSV values.

| paper time | max |ΔT| (°C) | max |ΔC| (kg/kg) |
|---:|---:|---:|
| 0.5 h | 3.953583190536847e-4 | 1.663045245736683e-6 |
| 1.0 h | 2.388971443224364e-3 | 7.972974228387386e-6 |
| 1.5 h | 4.093653740255832e-4 | 5.397997112410735e-6 |
| 2.0 h | 9.034566409127365e-5 | 5.718566997714447e-6 |
| 2.5 h | 8.071314489939141e-4 | 4.222319071045533e-6 |
| 3.0 h | 2.312629917469167e-4 | 2.948538489588870e-6 |

Over all solver nodes and all output times, the 0–3 h field L∞ differences are
`2.388971443224364e-3 °C` and `7.972974228387386e-6 kg/kg`; over 0–4 h they are
`8.936884727290817e-3 °C` and `1.643173166887557e-5 kg/kg`. The maximum difference
between the surface Robin fluxes over 0–4 h is `1.1998464344969761 W/m²` for heat
(at `14365 s`) and `6.112264004415e-11 kg/(m²·s)` for moisture (at `3137 s`). At
the paper times, the largest surface heat-flux difference is `0.0597242861 W/m²`
at `3600 s`; the largest paper-time surface moisture-flux difference is
`6.378379382723451e-12 kg/(m²·s)`.

### Recommendation and human decision

- **Recommendation:** linear, because it passes through the same official knots and
  is materially simpler and more transparent; the comparison is not small enough to
  call linear and PCHIP numerically equivalent.
- **Risk if chosen:** linear has slope changes at attachment knots and may miss a
  physically smooth between-knot trend.
- **Risk if rejected:** PCHIP changes paper-point fields and surface heat flux,
  increases implementation assumptions, and requires a new canonical production run
  before any paper/result extraction.
- **Required human decision:** choose linear, choose PCHIP, or request more interpolation
  evidence. Status: `D-Q2-INTERPOLATION = RECOMMENDED_FOR_HUMAN_APPROVAL`.

## D3 h / hm posture

### Official facts and source posture

The current Q2/Appendix 3 asset does not establish a new independent Q2 value for
`h` or `hm`. The values `h=25 W/(m²·K)` and `hm=8e-7 m/s` are therefore
`CARRIED-FORWARD MODELING ASSUMPTIONS`, not “official Q2 parameters” and not fitted
coefficients.

### Experimental evidence

The existing `EXP-Q2-014-BC-SENSITIVITY` used independent ±10% changes at 0–6 h,
with `dt=1 s`; its classification is low for h and medium for hm. The targeted
`EXP-Q2-021-DECISION-TARGETS-BC-LONG` used the same geometry and model to add 3 h
and 72 h checkpoints at `dt=2 s`. Its long screen is not a production-accuracy run.

| perturbation | 3 h max |ΔT| (K) | 3 h max |ΔC| | 72 h max |ΔT| (K) | 72 h max |ΔC| | passive bracket shift vs targeted base (s) | impact class |
|---|---:|---:|---:|---:|---:|---:|
| h -10% | 0.0507904317 | 0.0045451025 | 1.2846613e-11 | 6.0316724e-6 | +32 | LOW |
| h +10% | 0.0340800346 | 0.0036196451 | 1.5063506e-11 | 4.9138469e-6 | -26 | LOW |
| hm -10% | 0.0059201299 | 0.0796600649 | 2.1373125e-11 | 5.1013868e-4 | +2646 | MEDIUM |
| hm +10% | 0.0052665070 | 0.0709855842 | 2.3760549e-11 | 3.9354628e-4 | -2076 | MEDIUM |

The targeted base passive bracket is `205912–205914 s`; perturbation shifts above
are relative to that `dt=2 s` base and should not be compared as sub-second event
precision. At 72 h, h effects have largely decayed, while hm still changes the
moisture field by about `4–5×10^-4` and shifts the passive bracket by roughly
`35–44 min`. The passive bracket remains diagnostic only.

### Recommendation and human decision

- **Recommendation:** carry forward `h=25` and `hm=8e-7` as explicit modeling
  assumptions, do not fit them to the Q2 field, and retain the ±10% sensitivity and
  hm event-time impact in limitations/sensitivity text.
- **Risk if chosen:** any real coefficient bias, especially in hm, can materially
  change moisture and threshold timing.
- **Risk if rejected:** replacing them without an official source or independent
  calibration would add an untraceable parameter change and possible overfit.
- **Required human decision:** approve carried-forward posture, replace with a sourced
  value, or request calibration evidence. Status:
  `D-Q2-BOUNDARY-COEFFICIENTS = RECOMMENDED_FOR_HUMAN_APPROVAL`.

## D4 Interface averaging

### Official facts and team-reference proposal

The problem statement does not prescribe the face average for variable radial
coefficients. Arithmetic and harmonic means are both implementable. Arithmetic is a
team-reference option because it is simpler; harmonic is the current canonical
production lineage and is conservative for a coefficient contrast.

### Manufactured benchmark and short Q2 evidence

`EXP-Q2-015-INTERFACE-MEAN` reports both consistency/conservation benchmark runs as
passing. At manufactured `n=80`, the L∞ errors are:

| face mean | heat L∞ | moisture L∞ |
|---|---:|---:|
| arithmetic | 1.081798955073765e-4 | 1.557386493879243e-4 |
| harmonic | 1.082294989589450e-4 | 1.558345875894409e-4 |

Manufactured observed orders remain approximately first-order for both choices:
heat `1.0391/1.0223/1.0118`, moisture `1.0407/1.0229/1.0120`. In real Q2 over 0–3 h,
arithmetic versus harmonic has max differences `1.368523840028502e-6 K` and
`4.947719021153318e-7 kg/kg`; both short runs conserve and pass residual checks.

### Long-horizon evidence

The targeted arithmetic run uses the same `n=80, dt=0.25 s`, ENV-A, linear,
BDF2 configuration as the canonical harmonic run and compares exact checkpoint
nodes. Source: `experiments/EXP-Q2-021-DECISION-TARGETS/`.

| time | max |ΔT| (°C) | max |ΔC| | center signed ΔT / ΔC | r=1.0 signed ΔT / ΔC | r=1.5 signed ΔT / ΔC | surface signed ΔT / ΔC |
|---:|---:|---:|---|---|---|---|
| 6 h | 2.0017409952e-9 | 1.5211921978e-6 | +2.0017410e-9 / -1.3613137e-6 | +1.7715820e-9 / -1.5211922e-6 | +1.4370016e-9 / -1.0476817e-6 | +9.5366204e-10 / +1.1197705e-6 |
| 24 h | 3.8085090637e-12 | 1.3957089296e-4 | -1.1368684e-13 / -2.9590680e-5 | -1.7053026e-13 / -3.9250372e-5 | 0 / -5.9508341e-5 | -3.8085091e-12 / +7.0066989e-6 |
| 48 h | 4.8316906032e-12 | 1.2652592983e-4 | +2.5579538e-12 / -3.6668303e-5 | +3.9221959e-12 / -4.3716443e-5 | +3.1263880e-12 / -5.9032018e-5 | +4.5474735e-12 / -2.0035862e-6 |
| 72 h | 5.4569682106e-12 | 1.0147461116e-4 | -3.1832314562e-12 / -3.3237486031e-5 | -3.1263880373e-12 / -3.8527076803e-5 | -4.2064130e-12 / -5.0148107170e-5 | 4.1495696e-12 / -1.5708367903e-6 |

The complete signed/absolute point table for 6/24/48/72 h is
`experiments/EXP-Q2-021-DECISION-TARGETS/interface_long_target_points.csv`. The
long moisture difference is not far below the proposed Q2 field gate in D5; the
previous short-horizon arithmetic recommendation is therefore not sufficient to
freeze arithmetic for production.

### Recommendation and human decision

- **Recommendation:** retain harmonic for the canonical production candidate, because
  it is already the recovered production lineage and the long-horizon moisture
  difference from arithmetic reaches `1.3957089296e-4 kg/kg`.
- **Risk if chosen:** harmonic is slightly more complex to explain and its benchmark
  error is microscopically larger than arithmetic in the manufactured test.
- **Risk if rejected:** choosing arithmetic would require a new canonical production
  run and could change long-horizon moisture values beyond the proposed numerical gate.
- **Required human decision:** approve harmonic, approve arithmetic with a new run, or
  request additional face-flux evidence. Status:
  `D-Q2-INTERFACE-MEAN = RECOMMENDED_FOR_HUMAN_APPROVAL`.

## D5 Q2 numerical accuracy criterion

This is a proposed Q2 production gate, not a claim that the present candidate has
already passed every item. It is separate from output formatting and from Q3 event
time precision.

### FIELD OUTPUT CRITERION

1. Keep full floating-point precision internally and compare fields at the same
   physical time and radius; never compute an error from four-decimal output.
2. With spatial and temporal dimensions varied separately, require the estimated
   absolute numerical uncertainty over the complete declared Q2 production interval
   to be at most `2.5e-5 °C` for temperature and `2.5e-5 kg/kg` for moisture, for
   both field `L∞` and node/time `L2-RMS` summaries. The `2.5e-5` proposal is a
   quarter of one four-decimal output unit, leaving a numerical margin rather than
   merely reusing Q1's half-unit number.
3. Report adjacent observed orders from the actual refinement table. For a BE study,
   the asymptotic target is approximately first order; for BDF2, the target is
   approximately second order after startup. A curve without an order table is not
   sufficient evidence. The existing formal short-horizon evidence is separated:
   `EXP-Q2-005` BE time orders are temperature
   `1.047/1.099/1.222/1.585` and moisture `0.999/1.072/1.206/1.577`;
   `EXP-Q2-006` space orders are temperature `2.093/2.327` and moisture
   `1.036/1.411`.
4. The final production validation must state the complete time interval used for
   L∞/L2 aggregation, not only selected checkpoints. Long-horizon checkpoint proxy
   curves in `EXP-Q2-017` are stability evidence, not a replacement for that gate.

### LONG-HORIZON DIAGNOSTICS

Record `max C`, mean `C`, surface `C`, center `C`, `D(C,T)` range, Picard count,
nonlinear residual, linear/time-step residual, mass/heat balance residual and Robin
boundary residual. Require finite fields, positive moisture and finite positive
diffusivity throughout. These diagnostics guard physical/numerical integrity; they
do not substitute for the field uncertainty criterion.

### REPORTING AND EVENT-TIME DIAGNOSTICS

- Four-decimal rounding is applied only to the official output workbook and is not a
  numerical acceptance test.
- Q2 records the passive threshold bracket as an observer only. Event-time tolerance,
  interpolation of the threshold crossing and the formal Q3 event-time precision are
  left for Q3; Q2 does not freeze that precision.
- Status: `D-Q2-NUM-ACCURACY = RECOMMENDED_FOR_HUMAN_APPROVAL`.

## D6 Production horizon policy

### Official facts and workflow interpretation

- Official Q2 asks for the whole drying process, but does not by itself define a
  numerical stop in this workflow.
- Official Q3 asks for the time at which all `C < 0.15 kg/kg`.
- The current `205913–205913.25 s` bracket is a passive Q2 diagnostic, not a Q3 answer.
- “2–3 days” is background context, not an official fixed stop of 72 h.

### Rule-driven recommendation

Pre-register a production horizon as

`H_prod = ceil(t_passive_bracket_end + H_safety_tail)`

with a human-approved safety tail and a lower bound sufficient for Q2's whole-process
use. The horizon must be chosen before extracting paper/workbook results and must not
be cropped after looking at the field. The current validated envelope candidate is
`H_prod=259200 s (72 h)`, because it ends `53286.75 s` (about `14.80 h`) after the
ENV-A passive bracket. This is a recommended envelope, not “official fixed stop =
72 h”; the human may select another pre-registered tail.

### Cost and reuse estimate

Under the current canonical sampler, including `t=0`, the expected long-format field
rows are `259201 × 21 = 5443221` per field. A wide two-sheet workbook would contain
`259202` rows including the header and `22` columns per sheet, or about `11404888`
cells across temperature and moisture. The current recovered CSV is
`367089259 bytes`; the current raw CSV is `373569614 bytes`, and both are evidence
artifacts, not workbook files. Scaling the verified Q1 workbook size by the Q2 row
count gives a rough compressed `.xlsx` estimate of approximately `40–80 MB`; the
exact size must be measured only when an authorized candidate workbook is generated.
The five recorded ENV-A solver stages total approximately `1466.258559 s`
(`24.44 min`) at `n=80, dt=0.25 s`, before any future hardware/runtime variation.

One shared, pre-registered long run lets Q3 reuse the same canonical field and
checkpoint lineage, avoiding a second full solver run. Q3 may still perform its own
event-time analysis; it must not reinterpret this passive bracket as its final answer.

- **Risk if chosen:** a long fixed envelope costs storage and runtime, and may be
  longer than strictly needed for a Q2-only paper table.
- **Risk if rejected:** stopping near the passive bracket can omit a post-event safety
  tail and forces a second production run for Q3; treating 72 h as official without a
  rule would be an unsupported interpretation.
- **Required human decision:** approve the rule and safety tail, choose another rule,
  or request a cost/coverage study. Status:
  `D-Q2-PRODUCTION-HORIZON = RECOMMENDED_FOR_HUMAN_APPROVAL`.

## D7 Canonical recovered-data lineage

### Canonical source

The canonical run is `EXP-Q2-016-LONG-ENV-A-last-raw`: ENV-A last raw point held
constant after `14400 s`, `n=80`, `dt=0.25 s`, BDF2, linear interpolation, harmonic
face mean. Its status remains `RECOMMENDED_FOR_HUMAN_APPROVAL`.

The manifest `experiments/Q2_CANONICAL_DATA_MANIFEST.json` records each registered
file's project-relative path, SHA-256, role, status and exclusion reason. The recovered
samplers are:

- `official_samples_recovered.csv`: `RECOVERED_CANONICAL`, complete one-second grid;
- `diagnostics_1s_recovered.csv`: `RECOVERED_CANONICAL`, complete one-second keys;
- configuration, metrics, checkpoints, stage summaries, notes and figures:
  `CANONICAL`.

The raw files are retained for provenance and are not deleted:

- `official_samples.csv`: `NONCANONICAL_DUPLICATE`, because an interrupted resume
  appended duplicate `(time_s, radius_cm)` keys;
- `diagnostics_1s.csv`: `NONCANONICAL_DUPLICATE`, because an interrupted resume
  appended duplicate `time_s` keys.

`src/q2/lineage.py` provides `canonical_path()` and `canonical_csv_path()`. They
fail closed for unregistered files, `NONCANONICAL_INTERRUPTED`, and
`NONCANONICAL_DUPLICATE`, and verify SHA-256 by default. Q2 plotting and canonical
checkpoint comparison now use this guard. Future production plots, paper tables and
the authorized result2 candidate generator must use the guard; old sensitivity runs,
raw interrupted files and duplicate copies are not final-data sources.

- **Risk if chosen:** recovered data carry an explicit provenance event and depend on
  the documented first-key retention rule.
- **Risk if rejected:** consuming raw duplicates can silently double-count time/radius
  keys and contaminate figures, paper tables or a future workbook.
- **Required human decision:** approve the manifest/guard, request a different recovery
  rule, or request rerun. Status:
  `D-Q2-CANONICAL-LINEAGE = RECOMMENDED_FOR_HUMAN_APPROVAL`.

## Human approval table

| Decision ID | Recommended option | Alternative | Quantitative impact to review | Recommended status | Human action |
|---|---|---|---|---|---|
| D-Q2-ENVIRONMENT | ENV-A last raw, constant after 14400 s | ENV-B tail40 mean; team 50/0.05 | A/B temperature L∞ ≈0.16975 °C at long times; 72 h moisture L∞ ≈2.7757e-4; bracket shift +1121.5 s | `RECOMMENDED_FOR_HUMAN_APPROVAL` | APPROVE / REJECT / REQUEST MORE EVIDENCE |
| D-Q2-INTERPOLATION | Linear | PCHIP | 0–4 h max difference `8.9369e-3 °C`, `1.6432e-5 kg/kg`; heat-flux max `1.1998 W/m²` | `RECOMMENDED_FOR_HUMAN_APPROVAL` | APPROVE / REJECT / REQUEST MORE EVIDENCE |
| D-Q2-BOUNDARY-COEFFICIENTS | Carry forward h/hm as explicit assumptions | Replace/source/calibrate | hm ±10% gives 72 h moisture change `3.94–5.10e-4`; bracket shift `-2076/+2646 s` | `RECOMMENDED_FOR_HUMAN_APPROVAL` | APPROVE / REJECT / REQUEST MORE EVIDENCE |
| D-Q2-INTERFACE-MEAN | Harmonic | Arithmetic | Long moisture difference reaches `1.3957e-4`; short difference is below `5e-7` | `RECOMMENDED_FOR_HUMAN_APPROVAL` | APPROVE / REJECT / REQUEST MORE EVIDENCE |
| D-Q2-NUM-ACCURACY | Quarter-output-unit field gate plus separate L∞/L2/order audit | Other documented gate | Proposed `2.5e-5 °C` and `2.5e-5 kg/kg`; event precision remains Q3 | `RECOMMENDED_FOR_HUMAN_APPROVAL` | APPROVE / REJECT / REQUEST MORE EVIDENCE |
| D-Q2-PRODUCTION-HORIZON | Rule-driven passive bracket + human safety tail; current candidate 72 h envelope | Other pre-registered horizon | 5,443,221 rows/field; rough workbook `40–80 MB`; measured solver stages `24.44 min` | `RECOMMENDED_FOR_HUMAN_APPROVAL` | APPROVE / REJECT / REQUEST MORE EVIDENCE |
| D-Q2-CANONICAL-LINEAGE | Recovered ENV-A files through fail-closed manifest guard | Rerun/recovery rule change | Raw duplicate rows retained but rejected; hashes enforced | `RECOMMENDED_FOR_HUMAN_APPROVAL` | APPROVE / REJECT / REQUEST MORE EVIDENCE |

## Integrity and repository boundary

- Q1 remains `FROZEN / COMPLETE`; its final workbook SHA-256 remains
  `06b67b1f688d84a701ac4d2f4b0f47a1624069877df6724faf071a48af177b5c`.
- Official source `A题/` remains immutable; `A题/A题.pdf` SHA-256 is
  `052d8014bff5727c019b72e44fdffaf5c145ce04050dd938baaf3527db331736` and
  `A题/附件/附件1.xlsx` SHA-256 is
  `7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7`.
- No `result2.xlsx` exists in `deliverables/candidate/` or `deliverables/final/`.
- Repository visibility is Public; this gate permits LOCAL COMMIT ONLY and no push.
