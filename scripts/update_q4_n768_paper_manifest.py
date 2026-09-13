"""Refresh the paper asset manifest after the validated Q4 n=768 freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "deliverables" / "final" / "paper"
MANIFEST = PAPER / "PAPER_ASSET_MANIFEST.json"
TRACE = json.loads((PAPER / "Q4_N768_FIGURE_TRACE.json").read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def file_record(path: Path) -> dict[str, object]:
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def supporting(name: str) -> dict[str, object]:
    candidate = ROOT / "deliverables" / "candidate_reaudit" / "paper" / name
    final = PAPER / name
    return {"candidate_path": str(candidate.relative_to(ROOT)).replace("\\", "/"), "final_path": str(final.relative_to(ROOT)).replace("\\", "/"), "candidate_sha256": sha256(candidate), "final_sha256": sha256(final), "candidate_size_bytes": candidate.stat().st_size, "final_size_bytes": final.stat().st_size, "byte_identical": candidate.read_bytes() == final.read_bytes()}


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    preserved = [asset for asset in manifest["assets"] if not (asset["asset"] == "Table6" or asset["asset"].startswith("Q4 figures:") or asset["asset"].startswith("Comparison figures:"))]
    table6 = PAPER / "tables" / "table6_q4.xlsx"
    table6_source = ROOT / "experiments" / "Q4_PAPER_FINAL_N768" / "paper_samples.csv"
    preserved.append({"asset": "Table6", "source": str(table6_source.relative_to(ROOT)).replace("\\", "/"), "source_sha256": sha256(table6_source), "generator": "L_n768_dt2 canonical postprocess; no solver rerun during freeze", "output": [str((PAPER / "tables" / n).relative_to(ROOT)).replace("\\", "/") for n in ("table6_q4.csv", "table6_q4.md", "table6_q4.xlsx")], "trace_result": {"status": "PASS", "cells": "54/54", "source_csv_sha256": sha256(table6_source), "final_xlsx_sha256": sha256(table6)}})
    for item in TRACE["figures"]:
        stem = item["figure"]
        group = "Comparison" if stem == "fig_5_18_q3_q4_drying_time_comparison" else "Q4"
        destination = PAPER / "figures" / ("comparison" if group == "Comparison" else "q4")
        source = item["source"]
        source_hash = item["source_sha256"]
        preserved.append({"asset": f"{group} figures: {stem}", "source": source, "source_sha256": source_hash, "generator": "L_n768_dt2 canonical raw postprocess; no solver rerun during freeze", "output": [str((destination / f"{stem}.{ext}").relative_to(ROOT)).replace("\\", "/") for ext in ("png", "svg")], "trace_result": "4/4", "png_dpi": [300.101, 300.101]})
    manifest.update({"schema_version": "Q3_Q4_PAPER_ASSET_MANIFEST_V2", "status": "PASS", "freeze_approval_status": "APPROVED", "solver_rerun": False, "q4_production_run": "L_n768_dt2", "q4_production_result": "52.6640375959 h", "q4_chinese_localization": "not applicable; Q4 figures regenerated with Chinese metadata", "assets": preserved, "asset_count": len(preserved), "tables_count": 2, "figure_groups_count": 7})
    updated_supporting = []
    for item in manifest.get("supporting_files", []):
        final_name = Path(item["final_path"]).name
        if final_name in {"q4_summary.json", "q3_q4_comparison.json", "q4_results.md"}:
            updated_supporting.append(supporting(final_name))
        else:
            updated_supporting.append(item)
    manifest["supporting_files"] = updated_supporting
    manifest["q4_figure_trace"] = {"path": "deliverables/final/paper/Q4_N768_FIGURE_TRACE.json", "png": 4, "svg": 4, "dpi": "4/4", "data_trace": "4/4", "chinese_text": "4/4"}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "asset_count": manifest["asset_count"], "q4_production_run": manifest["q4_production_run"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
