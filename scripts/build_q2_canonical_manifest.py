"""Build the Q2 canonical-data lineage manifest from the recovered run."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RUN = ROOT / "experiments" / "EXP-Q2-016-LONG-ENV-A-last-raw"
MANIFEST = ROOT / "experiments" / "Q2_CANONICAL_DATA_MANIFEST.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def entry(filename: str, status: str, role: str, reason: str) -> dict:
    path = RUN / filename
    if not path.is_file():
        raise FileNotFoundError(path)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "status": status,
        "role": role,
        "reason": reason,
    }


def main() -> None:
    metadata = [
        ("config.json", "CANONICAL", "solver_config", "Canonical ENV-A run configuration."),
        ("metrics.json", "CANONICAL", "run_metrics", "Metrics point to the recovered sampler for downstream use."),
        ("output_recovery_metrics.json", "CANONICAL", "lineage_audit", "Records raw duplication and recovered-key validation."),
        ("output_recovery_notes.md", "CANONICAL", "lineage_notes", "Human-readable recovery provenance."),
        ("notes.md", "CANONICAL", "run_notes", "Canonical run scope and non-workbook boundary."),
        ("checkpoint_21600s.json", "CANONICAL", "checkpoint", "6 h checkpoint."),
        ("checkpoint_43200s.json", "CANONICAL", "checkpoint", "12 h checkpoint used for restart audit."),
        ("checkpoint_86400s.json", "CANONICAL", "checkpoint", "24 h checkpoint."),
        ("checkpoint_172800s.json", "CANONICAL", "checkpoint", "48 h checkpoint."),
        ("checkpoint_259200s.json", "CANONICAL", "checkpoint", "72 h checkpoint."),
        ("stage_21600s.json", "CANONICAL", "stage_diagnostics", "6 h stage summary."),
        ("stage_43200s.json", "CANONICAL", "stage_diagnostics", "12 h recovery stage summary."),
        ("stage_86400s.json", "CANONICAL", "stage_diagnostics", "24 h stage summary."),
        ("stage_172800s.json", "CANONICAL", "stage_diagnostics", "48 h stage summary."),
        ("stage_259200s.json", "CANONICAL", "stage_diagnostics", "72 h stage summary."),
        ("temperature_center_surface.png", "CANONICAL", "figure", "Generated only from recovered canonical samples."),
        ("moisture_center_surface.png", "CANONICAL", "figure", "Generated only from recovered canonical samples."),
        ("official_samples_recovered.csv", "RECOVERED_CANONICAL", "canonical_sampler", "Complete one-second official-radius sampler; first row per (time_s,radius_cm) key retained."),
        ("diagnostics_1s_recovered.csv", "RECOVERED_CANONICAL", "canonical_diagnostics", "Complete one-second diagnostic sampler; first row per time_s key retained."),
        ("official_samples.csv", "NONCANONICAL_DUPLICATE", "raw_sampler", "Interrupted resume advanced beyond the old checkpoint and duplicate rows were appended; retained only for provenance."),
        ("diagnostics_1s.csv", "NONCANONICAL_DUPLICATE", "raw_diagnostics", "Interrupted resume appended duplicate diagnostic times; retained only for provenance."),
    ]
    entries = [entry(*item) for item in metadata]
    recovered = [item["path"] for item in entries if item["status"] == "RECOVERED_CANONICAL"]
    raw = [item["path"] for item in entries if item["status"].startswith("NONCANONICAL_")]
    payload = {
        "manifest_version": "Q2_CANONICAL_DATA_MANIFEST_V1",
        "generated_by": "scripts/build_q2_canonical_manifest.py",
        "canonical_run": {
            "run_id": "EXP-Q2-016-LONG-ENV-A-last-raw",
            "interpretation": "ENV-A: Attachment 1 last raw point held constant after 14400 s",
            "horizon_s": 259200.0,
            "status": "RECOMMENDED_FOR_HUMAN_APPROVAL",
            "production_consumers": ["Q2 figures", "paper tables", "future result2 candidate generator"],
        },
        "canonical_recovered_files": recovered,
        "noncanonical_interrupted_or_duplicate_files": raw,
        "consumer_policy": {
            "required_loader": "src.q2.lineage.canonical_path / canonical_csv_path",
            "reject_noncanonical": True,
            "raw_files_retained": True,
            "result2_written": False,
        },
        "status_vocabulary": [
            "CANONICAL",
            "RECOVERED_CANONICAL",
            "NONCANONICAL_INTERRUPTED",
            "NONCANONICAL_DUPLICATE",
        ],
        "entries": entries,
    }
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(MANIFEST.relative_to(ROOT)), "entries": len(entries), "recovered": recovered, "raw": raw}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
