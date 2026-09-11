"""Replace the validation-era Q2 manifest with the approved production lineage."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "experiments" / "Q2_CANONICAL_DATA_MANIFEST.json"
FREEZE = ROOT / "experiments" / "Q2_FREEZE_RUN"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def main() -> int:
    if not FREEZE.is_dir() or not (FREEZE / "metrics.json").is_file():
        raise SystemExit("Q2_FREEZE_RUN production metrics are missing")
    metrics = json.loads((FREEZE / "metrics.json").read_text(encoding="utf-8"))
    if metrics.get("status") != "PRODUCTION_RUNS_COMPLETE":
        raise SystemExit("Q2 production runs are not complete")
    run1_sample = FREEZE / "run_1" / "official_samples.csv"
    run2_sample = FREEZE / "run_2" / "official_samples.csv"
    if not run1_sample.is_file() or not run2_sample.is_file():
        raise SystemExit("Q2 production sampled outputs are missing")

    old = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {"entries": []}
    entries = []
    for entry in old.get("entries", []):
        copied = dict(entry)
        old_status = copied.get("status")
        if old_status in {"CANONICAL", "RECOVERED_CANONICAL"}:
            copied["status"] = "VALIDATION_ONLY"
            copied["reason"] = "validation-era Q2 artifact; excluded from formal production results"
        entries.append(copied)

    production_files = [
        (FREEZE / "config.json", "PRODUCTION_CANONICAL", "frozen production configuration"),
        (FREEZE / "environment.json", "PRODUCTION_CANONICAL", "frozen production environment rule"),
        (FREEZE / "metrics.json", "PRODUCTION_CANONICAL", "production run metrics"),
        (FREEZE / "validation.json", "PRODUCTION_CANONICAL", "production validation gate record"),
        (FREEZE / "output_hashes.json", "PRODUCTION_CANONICAL", "production output hashes"),
        (FREEZE / "run_1/official_samples_raw.csv", "PRODUCTION_CANONICAL", "run 1 raw sampled output including internal t=0 layer"),
        (FREEZE / "run_1/official_samples.csv", "PRODUCTION_CANONICAL", "sole formal Q2 result source; t=1..final_horizon official grid"),
        (FREEZE / "run_1/diagnostics_1s.csv", "PRODUCTION_CANONICAL", "run 1 one-second diagnostics"),
        (FREEZE / "run_1/checkpoint_final.json", "PRODUCTION_CANONICAL", "run 1 final checkpoint"),
        (FREEZE / "run_2/official_samples_raw.csv", "DETERMINISM_REFERENCE", "independent run 2 raw output"),
        (FREEZE / "run_2/official_samples.csv", "DETERMINISM_REFERENCE", "independent run 2 sampled output"),
        (FREEZE / "run_2/diagnostics_1s.csv", "DETERMINISM_REFERENCE", "independent run 2 diagnostics"),
        (FREEZE / "run_2/checkpoint_final.json", "DETERMINISM_REFERENCE", "independent run 2 final checkpoint"),
    ]
    for path, status, reason in production_files:
        if not path.is_file():
            raise SystemExit(f"missing production manifest file: {path}")
        entries.append({"path": rel(path), "sha256": sha256(path), "status": status, "role": "q2_production", "reason": reason})

    # Avoid duplicate entries if this script is deliberately re-run after an
    # interrupted documentation step, while keeping the operation fail-closed.
    deduplicated = {}
    for entry in entries:
        path = entry["path"]
        if path in deduplicated and deduplicated[path].get("sha256") != entry.get("sha256"):
            raise SystemExit(f"conflicting manifest entries for {path}")
        deduplicated[path] = entry
    entries = [deduplicated[path] for path in sorted(deduplicated)]
    final_horizon = metrics["production_horizon"]["final_horizon_s"]
    manifest = {
        "manifest_version": "Q2_CANONICAL_DATA_MANIFEST_V1",
        "generated_by": "scripts/build_q2_production_manifest.py",
        "canonical_run": {
            "run_id": "Q2_FREEZE_RUN/run_1",
            "interpretation": "approved ENV-B tail40 mean, constant post-14400 s environment",
            "horizon_s": final_horizon,
            "status": "PRODUCTION_CANONICAL",
            "production_result_source": "experiments/Q2_FREEZE_RUN/run_1/official_samples.csv",
        },
        "validation_only_roots": [
            "experiments/EXP-Q2-012-ENVIRONMENT",
            "experiments/EXP-Q2-013-INTERPOLATION",
            "experiments/EXP-Q2-014-BC-SENSITIVITY",
            "experiments/EXP-Q2-015-INTERFACE-MEAN",
            "experiments/EXP-Q2-016-LONG-ENV-A-last-raw",
            "experiments/EXP-Q2-017-LONG-TIME-PROXY",
            "experiments/EXP-Q2-018-ENV-COMPARISON",
            "experiments/EXP-Q2-019-RESTART-LONG",
            "experiments/EXP-Q2-020-BASELINE",
            "experiments/EXP-Q2-021-DECISION-TARGETS",
        ],
        "consumer_policy": {
            "required_loader_for_formal_results": "src.q2.lineage.production_canonical_path / production_csv_path",
            "reject_noncanonical": True,
            "formal_result_source_run": "experiments/Q2_FREEZE_RUN/run_1",
            "run_2_is_determinism_reference_only": True,
            "raw_files_retained": True,
        },
        "status_vocabulary": ["PRODUCTION_CANONICAL", "DETERMINISM_REFERENCE", "VALIDATION_ONLY", "NONCANONICAL_INTERRUPTED", "NONCANONICAL_DUPLICATE", "CANONICAL", "RECOVERED_CANONICAL"],
        "entries": entries,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "manifest": rel(MANIFEST), "formal_source": manifest["canonical_run"]["production_result_source"], "entries": len(entries), "run1_sha256": sha256(run1_sample), "run2_sha256": sha256(run2_sample)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
