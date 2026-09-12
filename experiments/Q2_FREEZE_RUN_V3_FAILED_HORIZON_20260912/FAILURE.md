# Q2 V3 failed predeclared-horizon attempt

- Status: `FAILED_PRODUCTION_ATTEMPT`
- The run started fresh from `t=0` with the V3 n=320/cluster3, early-5 s, dt=0.25 s production configuration.
- The run completed to the predeclared endpoint `228635 s`.
- The solver's first passive crossing was `[206935.0, 206935.25] s`, not the previously carried-forward bracket `[207034.5, 207034.75] s`.
- The run is retained for provenance only. It is not a delivery source, was not resumed, and must not be used to generate `result2.xlsx` or formal Q2 figures.
- The corrected V3 endpoint for the fresh production run is `ceil(206935.25)+21600 = 228536 s`.
