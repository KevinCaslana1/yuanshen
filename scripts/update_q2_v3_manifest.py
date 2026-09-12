"""Register the completed Q2 V3 run as the sole production-canonical source."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "experiments" / "Q2_CANONICAL_DATA_MANIFEST.json"
V3 = ROOT / "experiments" / "Q2_FREEZE_RUN_V3"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["generated_by"] = "scripts/update_q2_v3_manifest.py"
    payload["canonical_run"] = {
        "run_id": "Q2_FREEZE_RUN_V3/run_1",
        "interpretation": "authorized V3 ENV-B production run; integer-second official lattice",
        "horizon_s": 228536,
        "status": "PRODUCTION_CANONICAL",
        "delivery_status": "VALIDATED_CANDIDATE_PENDING_HUMAN_FREEZE_APPROVAL",
        "attempt_status": "PASS_PRE_CANDIDATE_GATES",
        "production_result_source": "experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv",
    }
    previous_failures = [item for item in payload.get("failed_production_attempts", []) if item.get("root") not in {"experiments/Q2_FREEZE_RUN_V3_PREFLIGHT_BLOCKED_20260912", "experiments/Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912", "experiments/Q2_FREEZE_RUN_V3_POSTPROCESS_FAILURE_20260912"}]
    payload["failed_production_attempts"] = [
        *previous_failures,
        {
            "root": "experiments/Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912",
            "status": "FAILED_PRODUCTION_ATTEMPT",
            "delivery_status": "NOT_DELIVERY_SOURCE",
            "reason": "Fresh V3 numerical run used a carried-forward horizon before independently confirming the passive bracket; it completed to 228635 s but bracketed [206935.0,206935.25] s, so it was archived and not resumed.",
        },
        {
            "root": "experiments/Q2_FREEZE_RUN_V3_POSTPROCESS_FAILURE_20260912",
            "status": "FAILED_PRODUCTION_ATTEMPT",
            "delivery_status": "NOT_DELIVERY_SOURCE",
            "reason": "A non-numerical transition-probe writer omitted r=1.9 cm after corrected Run 1 integration; the partial probe file is provenance only and the completed numerical outputs were retained.",
        },
        {
            "root": "experiments/Q2_FREEZE_RUN_V3_PREFLIGHT_BLOCKED_20260912",
            "status": "FAILED_PRODUCTION_ATTEMPT",
            "delivery_status": "NOT_DELIVERY_SOURCE",
            "reason": "A preflight-only source-commit expectation mismatch stopped before numerical execution; no production result was consumed.",
        },
    ]
    payload["formal_certification"]["delivery_source_established"] = True
    payload["formal_certification"]["result2_generated"] = True
    payload["formal_certification"]["q3_q4_started"] = False
    payload["consumer_policy"]["formal_result_source_run"] = "experiments/Q2_FREEZE_RUN_V3/run_1"
    payload["consumer_policy"]["formal_result_source_status"] = "PRODUCTION_CANONICAL"
    payload["consumer_policy"]["failed_attempt_source_run"] = "experiments/Q2_FREEZE_RUN/run_1; experiments/Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912"
    payload["consumer_policy"]["run_2_is_determinism_reference_only"] = True

    entries = [entry for entry in payload.get("entries", []) if not entry.get("path", "").startswith("experiments/Q2_FREEZE_RUN_V3/")]
    files = [
        ("config.json", "solver_config", "VALIDATION_ONLY"),
        ("environment.json", "environment", "VALIDATION_ONLY"),
        ("input_hashes.json", "input_hashes", "VALIDATION_ONLY"),
        ("code_hashes.json", "code_hashes", "VALIDATION_ONLY"),
        ("accuracy_basis.json", "accuracy_basis", "VALIDATION_EVIDENCE_ONLY"),
        ("preflight.json", "preflight", "VALIDATION_ONLY"),
        ("determinism.json", "determinism", "VALIDATION_ONLY"),
        ("output_hashes.json", "output_hashes", "VALIDATION_ONLY"),
        ("metrics.json", "production_metrics", "VALIDATION_ONLY"),
        ("validation.json", "validation", "VALIDATION_ONLY"),
        ("lineage.json", "lineage", "VALIDATION_ONLY"),
        ("notes.md", "run_notes", "VALIDATION_ONLY"),
        ("run_1/official_samples_raw.csv", "internal_source", "PRODUCTION_CANONICAL"),
        ("run_1/official_samples.csv", "official_sampled_source", "PRODUCTION_CANONICAL"),
        ("run_1/diagnostics_1s.csv", "diagnostics", "PRODUCTION_CANONICAL"),
        ("run_1/checkpoint_final.json", "checkpoint", "PRODUCTION_CANONICAL"),
        ("run_1/metrics.json", "run_metrics", "PRODUCTION_CANONICAL"),
        ("run_2/official_samples_raw.csv", "internal_source", "DETERMINISM_REFERENCE"),
        ("run_2/official_samples.csv", "official_sampled_source", "DETERMINISM_REFERENCE"),
        ("run_2/diagnostics_1s.csv", "diagnostics", "DETERMINISM_REFERENCE"),
        ("run_2/checkpoint_final.json", "checkpoint", "DETERMINISM_REFERENCE"),
        ("run_2/metrics.json", "run_metrics", "DETERMINISM_REFERENCE"),
        ("candidate_validation.json", "candidate_validation", "VALIDATION_ONLY"),
        ("figure_validation.json", "figure_validation", "VALIDATION_ONLY"),
    ]
    for suffix, role, status in files:
        path = V3 / suffix
        if not path.is_file():
            raise FileNotFoundError(path)
        entries.append({"path": rel(path), "sha256": sha256(path), "status": status, "role": role, "reason": "sole authorized V3 production source" if status == "PRODUCTION_CANONICAL" else "V3 production audit artifact"})
    payload["entries"] = entries
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "canonical_run": payload["canonical_run"], "v3_entries_added": len(files)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
