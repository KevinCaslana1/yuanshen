# Q2 Accuracy Remediation

日期：2026-09-12  
范围：Q2 numerical accuracy remediation only；Q1 remains frozen，Q3/Q4 remain not started。

## Current status

`Q2 FORMAL-OUTPUT ACCURACY GATE = COMPLETE / WAITING FOR V3 FREEZE RUN AUTHORIZATION`。

The original production attempt remains a historical failed provenance run. The authorized formal-output remediation now certifies the declared integer-second transition lattice, early official lattice and selected long-horizon points. The n=640 V2 full-horizon attempt remains aborted for impractical runtime and is not reused as a source. A non-output first-post-transition temperature probe remains above the field criterion, but it is bounded and does not propagate to formal output. `result2.xlsx` and formal Q2 figures remain intentionally ungenerated until a separate V3 freeze-run authorization.

## 1. Original accuracy metric audit

The old production source was Candidate A, actual 98 cells, `dt=.25 s`, ENV-B, linear interpolation, harmonic interfaces, and fresh `t=0` runs. The two dimensions were compared independently:

| Quantity | Reference | Raw L∞ | Raw L2 RMS | Interpretation |
|---|---|---:|---:|---|
| Temperature, temporal | production vs `dt=.125 s` | `1.9082196854469657e-4 °C` | `4.849128315172295e-7 °C` | time raw difference |
| Moisture, temporal | production vs `dt=.125 s` | `1.0007524800181855e-4 kg/kg` | `4.884745210583248e-8 kg/kg` | time raw difference |
| Temperature, spatial | production vs `n=160` | `5.745306611970591e-5 °C` | `4.400124076121024e-6 °C` | space raw difference |
| Moisture, spatial | production vs `n=160` | `2.0357404664261836e-4 kg/kg` | `3.0182278875418313e-5 kg/kg` | space raw difference |

These are fine/coarse raw differences. They are not Richardson uncertainties. The componentwise conservative envelope is the maximum of the independent dimension estimates: T `1.9082196854469657e-4 °C`, C `2.0357404664261836e-4 kg/kg`; they are not added together. The old observed orders T/C=`1.6685/3.0631` are not used as optimistic Richardson orders; C above the expected BDF2 asymptotic order is treated as a warning, not as evidence of a third-order method.

## 2. Frozen transition convention and diagnosis

The approved environment remains unchanged:

- `t <= 14400 s`: Attachment 1 piecewise linear interpolation.
- `t > 14400 s`: constant `(T_inf,C_inf)=(49.99525 °C,0.049988 kg/kg)`.
- At `14400 s`, Attachment 1 is `(50.165 °C,0.04986 kg/kg)`, so the approved input jump is `(-0.16975 °C,+0.000128 kg/kg)`.

The original solver used BDF2 on the first post-transition step when history existed. `H-Q2-ACC-T-001` records the numerical hypothesis that this crosses a boundary-condition discontinuity with an incompatible multistep history. The tested remedy is a numerical BE restart exactly at `14400 s`; it does not smooth or alter the environment.

`EXP-Q2-ACC-T-TRANSITION` shows that event-aligned restart reduces the common-time local raw bounds. The finest adjacent common-time bound is T `8.143186960296589e-7 °C`, C `1.5011414333798712e-10 kg/kg`; the corresponding current-method bounds are T `4.2051636739870446e-5 °C`, C `1.0275578943286234e-8 kg/kg`. Residuals and Picard counts did not worsen in that study.

The comparison is carefully scoped: each dt has a different first post-transition time. Therefore a common integer-time comparison does not certify the explicit `14400+dt` probe. In the later n=320 candidate regression, the candidate/reference temperature difference at `14400.25 s,r=2.0 cm` is `2.2991211631051556e-4 °C`; it decays over the next internal steps. The maximum over formal integer times `14390..14500 s` is T `1.55375452663975e-5 °C` and C `3.1402255240564614e-9 kg/kg`, below the formal gate. The local probe is retained as an internal diagnostic and does not block delivery under the newly authorized scope.

## 3. Q2 initial compatibility

`EXP-Q2-ACC-C-INITIAL` independently recomputed the Q2 initial condition and Robin condition:

| Quantity | Value |
|---|---:|
| Initial `C0` | `2.55 kg/kg` |
| `C_inf(0)` | `0.01963 kg/kg` |
| `hm` | `8e-7 m/s` |
| `D(C0,T0)` | `5.641680373025664e-9 m²/s` |
| Discrete initial diffusion flux | `0 kg/(m²·s)` |
| Robin flux | `2.0242959999999997e-6 kg/(m²·s)` |
| Internal-minus-Robin residual | `-2.0242959999999997e-6 kg/(m²·s)` |

Disposition: `INCOMPATIBLE_INITIAL_DATA_AND_ROBIN_CONDITION`, scoped only as a Q2 numerical initial-layer finding. The official initial condition, `hm`, `D`, and surface environment were not changed.

## 4. Separate spatial and temporal evidence

### Spatial isolation

With `dt=.015625 s` fixed through `2 s`, the actual clustered grids and raw differences were:

- n=320 → n=640, cluster power 2: C L∞ `5.1707227172848036e-5 kg/kg` and T L∞ `1.2754446743201697e-7 °C`.
- Further n=320 → n=640 comparison: C L∞ `1.297979618852807e-5 kg/kg` and T L∞ `3.199704678991111e-8 °C`.
- C error maxima are at the surface `r=2.0 cm`; center/interior values are at machine-level differences in the recorded radius set.

The stronger-clustering candidate n=320, `cluster_power=3` has 339 cells and minimum `dr=6.103515609590104e-10 m`. Against n=640, `cluster_power=2` (658 cells), its 0–2 s raw L∞ is T `1.0052019661088707e-8 °C`, C `2.5626144490864533e-6 kg/kg`. This is promising early spatial evidence, not a long-horizon approval.

### Temporal isolation

With the spatial grid fixed, the n=320 temporal sequence had raw T/C L∞:

| Pair | T L∞ (°C) | C L∞ (kg/kg) |
|---|---:|---:|
| `.25 → .125 s` | `3.7888153769927158e-6` | `1.299097893888046e-3` |
| `.125 → .0625 s` | `1.3447110518427507e-6` | `3.6776039694341733e-4` |
| `.0625 → .03125 s` | `3.5803554965241347e-7` | `4.996966040682338e-5` |

The supplemental n=640 refinement `.015625 → .0078125 s` gives T `2.100205165334046e-8 °C` and C `2.652957554083457e-6 kg/kg`, with nested raw observed order T `2.0162147645348902` and C `1.9407953904464814`. These orders are used as convergence evidence only; the reported uncertainty remains the conservative fine/coarse difference.

The early-time policy (`dt=.015625 s` through `2 s`, BE on the step-size change, then `.25 s`) reproduces the uniform fine run exactly at the recorded early points. It is recorded in `EXP-Q2-NUM-REMEDY-C-TIME` as numerical evidence, not as an automatic production approval.

## 5. V2 short and transition regression

`EXP-Q2-V2-REGRESSION` used n=320, `cluster_power=3`, candidate dt `.25 s`, early dt `.015625 s` through `2 s`, ENV-B, harmonic interfaces, and BE restarts at the step-size and environment transitions. Both candidate and dt `.125 s` reference ran fresh from `t=0` through `14500 s`, covering 0–3 h and the transition window.

At formal integer output times in `14390..14500 s`, T/C maxima are `1.55375452663975e-5 °C` and `3.1402255240564614e-9 kg/kg`. The explicit first-post-step probe at `14400.25 s,r=2.0 cm` has T raw difference `2.2991211631051556e-4 °C`, followed by bounded decay and no integer-second contamination. The run itself completed with Picard histories `2/3/3/3` and `2/2/3/3` (min/median/p95/max); no nonconvergence occurred.

## 6. Full-horizon and lineage disposition

The old `Q2_FREEZE_RUN` remains the failed production provenance and is not a delivery source. The new n=640 `Q2_FREEZE_RUN_V2` attempt was fresh, reached approximately `888 s` simulated time, and was stopped because the measured runtime made a full-horizon double run impractical. It has no complete metrics, validation, Run2, candidate workbook, or formal result source. It must not be resumed or overwritten.

Because the full-horizon V2 run was not completed, it is not a full-horizon n=640 proof and no production result source is established. The new certification is intentionally scoped according to `D-Q2-ACCURACY-SCOPE`; it does not silently promote the old failed run or the aborted V2 partial files into a result source. A future V3 attempt must use a new directory, fresh starts, the unchanged `2.5e-5` criterion, determinism, residual, sampler and lineage validation.

## 7. Formal-output certification result

`D-Q2-ACCURACY-SCOPE` separates delivery points from internal integrator probes. The complete evidence packet is `experiments/Q2_ACCURACY_REMEDIATION/accuracy_confirmation_v3.json`.

| Certified scope | Temperature raw/conservative bound | Moisture raw/conservative bound | Result |
|---|---:|---:|---|
| Transition integer seconds 14395–14500, six radii | `1.55375452663975e-5 °C` | `3.1402255240564614e-9 kg/kg` | PASS |
| Early formal times, all 21 official radii | `7.116765686987492e-6 °C` | `1.0270424274150258e-5 kg/kg` | PASS |
| Targeted long 3–48 h, n=640 localized reference | `1.2509725024756335e-6 °C` | `2.987415287369899e-6 kg/kg` | PASS |
| Passive-event integer neighborhood and final point, n=160 screen | finite and below gate | `2.008097424559263e-5` at 207033 s; `1.892403267497733e-5` at final | PASS |

The internal transition peak is `2.2991211631051556e-4 °C` at `14400.25 s,r=2.0 cm`; it decays at the retained internal probes and does not contaminate `14401 s` or later formal points. The early same-policy audit with fine startup only through `2 s` had C L∞ `4.723355270153107e-5 kg/kg` at `t=3 s,r=2.0 cm`; extending the fine startup window through `5 s` reduced the certified maximum to `1.0270424274150258e-5 kg/kg`. This is evidence for a step-policy transient, not sudden physical accuracy improvement.

The targeted long certificate is explicitly not an n=640 full-horizon convergence proof. It combines a new continuous n=320 candidate screen, a new n=640 reference through 48 h, a new n=160 screen for the passive/final tail, and previously completed 0–72 h stability evidence, with unchanged ENV-B, physics, IC, harmonic averaging and BDF2 elements recorded in the experiment metrics.

## Final disposition

`Q2 FORMAL-OUTPUT ACCURACY GATE COMPLETE`
`WAITING FOR Q2 V3 FREEZE RUN AUTHORIZATION`
`DO NOT GENERATE RESULT2 BEFORE THAT AUTHORIZATION`

Q1 = FROZEN / COMPLETE  
Q3 = NOT STARTED  
Q4 = NOT STARTED
