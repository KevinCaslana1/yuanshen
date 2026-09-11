# EXP-Q1-SURFACE-DECAY signed-error audit

This audit keeps both the signed pointwise error `e=C_test-C_ref` and `abs(e)`. The test is N640, the reference is N1280, both with `dt=0.0625 s`; positions 1.9 cm and the literal 2.0 cm surface are both included. The CSV values are full-precision floats. The signed plot is direct data with a zero line; the absolute plot uses semilogy and masks only exact non-positive points for display, without replacing their CSV values by epsilon.

The historical `surface_moisture_error_decay.svg` is preserved; its legacy custom SVG uses a linear y-axis. The new `absolute_error_semilogy.svg` is the explicit semilogy audit artifact, and the frozen final figure generator's semilogy output was not regenerated in this audit.
