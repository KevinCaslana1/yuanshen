"""Final read-only release audit for the Q2 V3 validated candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "experiments" / "Q2_FREEZE_RUN_V3"
CANDIDATE = ROOT / "deliverables" / "candidate" / "result2.xlsx"
FINAL = ROOT / "deliverables" / "final" / "result2.xlsx"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    validation = json.loads((V3 / "validation.json").read_text(encoding="utf-8"))
    candidate_validation = json.loads((V3 / "candidate_validation.json").read_text(encoding="utf-8"))
    figure_validation = json.loads((V3 / "figure_validation.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "experiments" / "Q2_CANONICAL_DATA_MANIFEST.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    if validation.get("status") != "ALL_DELIVERABLE_GATES_PASS":
        errors.append("V3 validation status is not ALL_DELIVERABLE_GATES_PASS")
    if not all(validation.get("gates", {}).values()):
        errors.append("one or more pre-candidate gates is false")
    if candidate_validation.get("status") != "PASS" or candidate_validation.get("candidate_sha256") != sha256(CANDIDATE):
        errors.append("candidate validation/hash mismatch")
    if figure_validation.get("status") != "PASS":
        errors.append("figure validation is not PASS")
    source_entry = next((entry for entry in manifest.get("entries", []) if entry.get("path") == "experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv"), None)
    if not source_entry or source_entry.get("status") != "PRODUCTION_CANONICAL":
        errors.append("V3 Run 1 is not the production-canonical manifest source")
    if FINAL.exists():
        errors.append("result2.xlsx exists in final before human approval")
    payload = {"status": "PASS" if not errors else "FAIL", "candidate": str(CANDIDATE.relative_to(ROOT)).replace("\\", "/"), "candidate_sha256": sha256(CANDIDATE), "manifest_canonical_source": source_entry, "final_result2_exists": FINAL.exists(), "q3_q4_started": validation.get("q3_q4_started"), "errors": errors}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
