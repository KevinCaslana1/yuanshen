# Q2 V3 post-processing failure

- Status: `POSTPROCESSING_FAILURE_ONLY`
- The V3 Run 1 numerical integration had already completed fresh from `t=0` to `228536 s` with raw samples, official samples, diagnostics, and checkpoint written.
- A first version of the non-production transition probe writer omitted `r=1.9 cm` and failed after writing a partial file.
- The partial file is retained here for provenance only. It is not a production source and was removed from the canonical Run 1 directory.
- The solver, environment logic, sampler, and numerical data were not changed by the recovery.
