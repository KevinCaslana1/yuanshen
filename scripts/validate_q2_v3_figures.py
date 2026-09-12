"""Validate Q2 V3 figure files and manifest traceability."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FIG_ROOT = ROOT / "figures" / "q2"
V3 = ROOT / "experiments" / "Q2_FREEZE_RUN_V3"
SOURCE = V3 / "run_1" / "official_samples.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    manifest_path = FIG_ROOT / "FIGURE_MANIFEST.json"
    validation_path = FIG_ROOT / "FIGURE_VALIDATION.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    trace = json.loads(validation_path.read_text(encoding="utf-8"))
    source_hash = sha256(SOURCE)
    errors: list[str] = []
    if manifest.get("status") != "PASS" or trace.get("status") != "PASS":
        errors.append("figure manifest or trace validation status is not PASS")
    if manifest.get("source_hash") != source_hash or trace.get("source_hash") != source_hash:
        errors.append("figure source hash mismatch")
    if manifest.get("source_run") != "experiments/Q2_FREEZE_RUN_V3/run_1":
        errors.append("figure source run is not V3 Run 1")
    if manifest.get("no_smoothing") is not True or manifest.get("no_numeric_interpolation") is not True:
        errors.append("figure manifest does not prohibit smoothing/interpolation")
    if len(manifest.get("figures", [])) != 11:
        errors.append("expected 11 Q2 figures")
    for figure in manifest.get("figures", []):
        for key in ("data_file", "png_path", "svg_path"):
            path = ROOT / figure[key]
            if not path.is_file():
                errors.append(f"missing {key}: {figure[key]}")
            elif key == "data_file" and sha256(path) != figure.get("data_sha256"):
                errors.append(f"data hash mismatch: {figure[key]}")
        if figure.get("source_hash") != source_hash or figure.get("no_smoothing") is not True or figure.get("no_numeric_interpolation") is not True:
            errors.append(f"lineage flag/hash mismatch: {figure.get('figure_id')}")
        png = ROOT / figure["png_path"]
        if png.is_file():
            with Image.open(png) as image:
                dpi = image.info.get("dpi", (0.0, 0.0))
                if not (float(dpi[0]) >= 299.0 and float(dpi[1]) >= 299.0):
                    errors.append(f"PNG dpi below 300: {figure['png_path']} ({dpi})")
    if trace.get("random_trace_count") != 30 or trace.get("random_trace_pass_count") != 30:
        errors.append("30-point figure traceability check did not pass")
    payload = {"status": "PASS" if not errors else "FAIL", "manifest": "figures/q2/FIGURE_MANIFEST.json", "manifest_sha256": sha256(manifest_path), "validation": "figures/q2/FIGURE_VALIDATION.json", "validation_sha256": sha256(validation_path), "figure_count": len(manifest.get("figures", [])), "random_trace": "30/30", "errors": errors}
    (V3 / "figure_validation.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = json.loads((V3 / "validation.json").read_text(encoding="utf-8"))
    audit["figures"] = payload
    audit["figures_generated"] = payload["status"] == "PASS"
    audit["status"] = "ALL_DELIVERABLE_GATES_PASS" if payload["status"] == "PASS" and audit.get("status") == "CANDIDATE_VALIDATION_PASS" else ("DELIVERABLE_GATES_BLOCKED" if payload["status"] != "PASS" else audit.get("status"))
    (V3 / "validation.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
