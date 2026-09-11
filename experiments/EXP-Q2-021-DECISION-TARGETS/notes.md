# EXP-Q2-021 Decision Targets

This experiment supplies only missing quantitative evidence for the Q2 human
model-decision packet. It does not select a final model and does not generate a
workbook.

- `boundary_long_target_metrics.json`: independent ±10% h/hm perturbations,
  targeted at 3 h and 72 h effects and passive bracket shifts. The screen uses
  `dt=2 s` and is not a production-accuracy certification.
- `interface_long_target_metrics.json`: arithmetic face mean at the canonical
  `n=80, dt=0.25 s` configuration, compared at canonical 6/24/48/72 h keys.
- `interface_long_target_points.csv`: signed and absolute differences at all 21
  radii and the four canonical long-horizon checkpoints.

The first interface post-processing attempt requested a non-canonical 10800 s
key and was rejected; the resolved failure remains in `docs/FAILURES.md`.
Raw and canonical production data are not overwritten. No Q3 stopping logic is
used, and `result2.xlsx` is not written.
