# EXP-Q2-016-LONG-ENV-B-tail40-mean

Q2 long-horizon boundary candidate comparison run. Uses Candidate A, clustered conservative FVM, BE startup/BDF2, harmonic face mean, linear interpolation, `dt=0.25 s`, `n=80`, and a constant post-14400 s environment set to the final-40-point mean (`T_inf=49.99525 °C`, `C_inf=0.049988 kg/kg`).

The run covers 0–259200 s with 6/24/48/72 h checkpoints and passive `C<0.15 kg/kg` event observation only; it never stops on that event and never writes `result2.xlsx`. It is retained as the ENV-B comparator for `EXP-Q2-018-ENV-COMPARISON`. See `config.json` and `metrics.json` for the input hash, code SHA, diagnostics, property ranges, and checkpoint evidence.
