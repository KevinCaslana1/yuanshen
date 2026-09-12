# Q4 moving-domain equation audit

- **physical PDE**: `MATCH` — Standalone reference uses cylindrical (1/r)d/dr(r D dC/dr) and heat analogue.
- **xi=r/R(t) transformation**: `MATCH` — Reference uses physical control volumes at current R and adds (Rdot/R) xi u_xi on RHS.
- **Rdot/R mesh-advection sign**: `MATCH` — Positive source alpha*xi*gradient corresponds to moving term on RHS.
- **1/r geometry**: `MATCH` — Face radius and annular control-volume factors are included; center row is symmetry.
- **variable k and D**: `MATCH` — Appendix 4 node properties and harmonic face coefficients are evaluated in Picard.
- **thermal Robin**: `MATCH` — Surface transfer is h=25 W/(m2 K), with outward-positive flux convention.
- **moisture Robin**: `MATCH` — Surface transfer is hm=8e-7 m/s and uses hm(C_s-C_inf).
- **xi boundaries**: `MATCH` — xi=0 uses center symmetry; xi=1 is the Robin surface control volume.
- **Jacobian/shrinking volume**: `MATCH` — Current-R annular volumes are used every step; R^2 volume balance is audited.
- **official Attachment 2 tail**: `MATCH` — After the last node the radius is held at the last prescribed value.

**Verification status:** `HOLD` because the independent n=144, dt=2 event is not four-decimal stable against n=96, dt=4.
