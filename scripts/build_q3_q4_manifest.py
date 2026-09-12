"""Build the Q3/Q4 candidate file manifest without changing numerical data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_entry(path: Path) -> dict[str, object]:
    return {"path": str(path.relative_to(ROOT)), "size_bytes": path.stat().st_size, "sha256": sha256(path)}


def main() -> None:
    candidate_files = [
        ROOT / "deliverables/candidate/result3.xlsx",
        ROOT / "deliverables/candidate/result4.xlsx",
        ROOT / "deliverables/candidate/tables/q3_table5.xlsx",
        ROOT / "deliverables/candidate/tables/q3_table5.csv",
        ROOT / "deliverables/candidate/tables/q3_table5.md",
        ROOT / "deliverables/candidate/tables/q4_table6.xlsx",
        ROOT / "deliverables/candidate/tables/q4_table6.csv",
        ROOT / "deliverables/candidate/tables/q4_table6.md",
    ]
    figure_files = sorted((ROOT / "deliverables/candidate/paper/figures").glob("fig_5_*.png")) + sorted((ROOT / "deliverables/candidate/paper/figures").glob("fig_5_*.svg"))
    payload = {
        "status": "CANDIDATE_COMPLETE_WAITING_FOR_HUMAN_Q3_Q4_FREEZE_APPROVAL",
        "q1": "FROZEN",
        "q2": "FROZEN",
        "q3": "CANDIDATE COMPLETE",
        "q4": "CANDIDATE COMPLETE",
        "q3_summary": json.loads((ROOT / "experiments/Q3_PRODUCTION/q3_summary.json").read_text(encoding="utf-8")),
        "q4_summary": json.loads((ROOT / "experiments/Q4_PRODUCTION/q4_summary.json").read_text(encoding="utf-8")),
        "validation": json.loads((ROOT / "deliverables/candidate/Q3_Q4_VALIDATION.json").read_text(encoding="utf-8")),
        "test_result": "65 passed",
        "candidate_files": [file_entry(path) for path in candidate_files],
        "figure_files": [file_entry(path) for path in figure_files],
        "protected_paths": ["A题/", "src/q1/", "src/q2/", "deliverables/final/result2.xlsx", "deliverables/final/figures/q2/"],
        "no_remote_push": True,
    }
    destination = ROOT / "experiments/Q3_Q4_CANDIDATE/manifest.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "deliverables/candidate/Q3_Q4_CANDIDATE_MANIFEST.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()
