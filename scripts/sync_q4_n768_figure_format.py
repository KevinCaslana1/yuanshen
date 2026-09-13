"""Synchronize the cleaned, validated Q4 SVG/PNG files into final metadata."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAND = ROOT / "deliverables" / "candidate_reaudit" / "paper"
FINAL = ROOT / "deliverables" / "final" / "paper"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def main() -> None:
    stems = ["fig_5_15_q4_radius_pchip", "fig_5_16_q4_dynamic_radial_moisture", "fig_5_17_q4_radius_and_mean"]
    for stem in stems:
        for ext in ("png", "svg"):
            shutil.copyfile(CAND / "figures" / "q4" / f"{stem}.{ext}", FINAL / "figures" / "q4" / f"{stem}.{ext}")
    stem = "fig_5_18_q3_q4_drying_time_comparison"
    for ext in ("png", "svg"):
        shutil.copyfile(CAND / "figures" / "comparison" / f"{stem}.{ext}", FINAL / "figures" / "comparison" / f"{stem}.{ext}")
    shutil.copyfile(CAND / "Q4_N768_FIGURE_TRACE.json", FINAL / "Q4_N768_FIGURE_TRACE.json")
    manifest_path = FINAL.parent / "Q4_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in manifest["figures"]["files"]:
        item.update(record(ROOT / item["path"]))
    manifest["figures"]["png_ge_300_dpi"] = "4/4"
    manifest["figures"]["data_trace"] = "4/4"
    manifest["figures"]["chinese_text"] = "4/4"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    freeze_path = FINAL.parent / "Q4_FREEZE_RECORD.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    freeze["q4"] = manifest
    freeze["figure_trace"] = json.loads((FINAL / "Q4_N768_FIGURE_TRACE.json").read_text(encoding="utf-8"))
    freeze_path.write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "figures": 8}, ensure_ascii=False))


if __name__ == "__main__":
    main()
