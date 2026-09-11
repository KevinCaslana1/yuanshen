# EXP-003 time-step convergence audit

Uniform radial grid is fixed at `dr=0.025 cm` (N=80). Only `dt` changes: 1, 0.5, 0.25, 0.125 s; `dt=0.0625 s` is the independent reference. Full-time CSVs contain signed and absolute errors at surface, r=1.5 cm, r=1.0 cm, and center. L∞ and discrete RMS-L2 are computed over 0--1800 s and over the t>=60 s tail.
