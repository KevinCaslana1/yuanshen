"""Write compact config/metrics/notes records for Q3/Q4 experiments."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    q3 = json.loads((ROOT / "experiments/Q3_PRODUCTION/q3_summary.json").read_text(encoding="utf-8"))
    q4 = json.loads((ROOT / "experiments/Q4_PRODUCTION/q4_summary.json").read_text(encoding="utf-8"))
    q3_dir = ROOT / "experiments/Q3_PRODUCTION"
    q4_dir = ROOT / "experiments/Q4_PRODUCTION"
    write(q3_dir / "config.json", {"experiment": "Q3_PRODUCTION", "status": "CANDIDATE", "threshold_kg_kg": 0.15, "input": "frozen Q2 V3 Run1 official_samples_raw.csv", "official_radii_cm": [i / 10 for i in range(21)], "regular_output_interval_s": 60.0, "endpoint_method": "local BE/Picard continuation from t=206935 s; 1/1024 s substeps; strict-below row", "forbidden": ["rerun full Q2", "modify deliverables/final/result2.xlsx", "write A题 or src/q2"], "source_q2_final_sha256": q3["frozen_q2_final_sha256"]})
    write(q4_dir / "config.json", {"experiment": "Q4_PRODUCTION", "status": "CANDIDATE", "threshold_kg_kg": 0.15, "properties": "Appendix 4", "radius_input": "A题/附件/附件2.xlsx", "radius_interpolation": "PchipInterpolator-compatible monotone cubic", "coordinate": "xi=r/R(t)", "n_intervals": 96, "dt_s": 4.0, "output_interval_s": 60.0, "boundary": "Robin; fixed physical positions outside current radius are blank; surface separate", "post_attachment_radius": "hold R_last=1.198 cm after 259200 s"})
    write(q3_dir / "metrics.json", q3)
    write(q4_dir / "metrics.json", q4)
    (q3_dir / "notes.md").write_text("# Q3 production candidate\n\nThe endpoint is a strict-below event row from local BE/Picard refinement, not a linear interpolation of two Excel rows. Candidate only; human freeze approval is pending.\n", encoding="utf-8")
    (q4_dir / "notes.md").write_text("# Q4 production candidate\n\nThe prescribed radius is evaluated in material coordinate xi=r/R(t) with monotone PCHIP and explicit outside-domain masking. Candidate only; human freeze approval is pending.\n", encoding="utf-8")


if __name__ == "__main__":
    main()

