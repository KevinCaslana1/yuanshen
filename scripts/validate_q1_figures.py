"""Validate the Q1 final figure package against the frozen source and final workbook."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import pickle
import random
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

import numpy as np
import openpyxl
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FREEZE_REFERENCE = ROOT / "experiments" / "Q1_FREEZE_RUN" / "run_1" / "internal_output_reference.pkl.gz"
FINAL_RESULT = ROOT / "deliverables" / "final" / "result1.xlsx"
FIG_ROOT = ROOT / "figures" / "q1"
EXPECTED_FREEZE_HASH = "f13667b5fe8e4c1e1a7635b18ab4c7aaa9e3fef5111b893a9ce79b6deb3fad17"
PAPER_TIMES_S = (100, 300, 600, 900, 1200, 1500, 1800)
PAPER_POSITIONS_CM = (0.0, 0.5, 1.0, 1.5, 2.0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rounded(value: float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def _time_index(times: np.ndarray, time_s: float) -> int:
    index = int(np.argmin(np.abs(times - time_s)))
    if abs(float(times[index]) - time_s) > 1.0e-9:
        raise ValueError(f"missing time {time_s}")
    return index


def _position_index(nodes: np.ndarray, position_cm: float) -> int:
    target = position_cm / 100.0
    index = int(np.argmin(np.abs(nodes - target)))
    if abs(float(nodes[index]) - target) > 1.0e-12:
        raise ValueError(f"missing position {position_cm} cm")
    return index


def validate() -> dict[str, Any]:
    errors: list[str] = []
    manifest_path = FIG_ROOT / "FIGURE_MANIFEST.json"
    if not manifest_path.is_file():
        return {"status": "FAIL", "errors": [f"missing {manifest_path}"], "checks": {}}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_hash = sha256(FREEZE_REFERENCE) if FREEZE_REFERENCE.is_file() else None
    if source_hash != EXPECTED_FREEZE_HASH:
        errors.append(f"freeze source hash mismatch: expected={EXPECTED_FREEZE_HASH} actual={source_hash}")
    if manifest.get("source_hash") != EXPECTED_FREEZE_HASH:
        errors.append("figure manifest source hash is not the protected freeze hash")

    figure_entries = manifest.get("figures", [])
    required_ids = {"FIG-Q1-01", "FIG-Q1-02", "FIG-Q1-03", "FIG-Q1-04", "FIG-Q1-05", "FIG-Q1-06", "FIG-Q1-V01a", "FIG-Q1-V01b", "FIG-Q1-V02"}
    actual_ids = {entry.get("figure_id") for entry in figure_entries}
    if actual_ids != required_ids:
        errors.append(f"figure ID mismatch: expected={sorted(required_ids)} actual={sorted(actual_ids)}")
    for entry in figure_entries:
        for key in ("figure_id", "title", "source_run", "source_hash", "variables", "time_selection", "radius_selection", "data_file", "data_sha256", "png_path", "svg_path", "generation_script", "commit", "generated_at"):
            if key not in entry:
                errors.append(f"{entry.get('figure_id', '<unknown>')} missing manifest field {key}")
        for key in ("data_file", "png_path", "svg_path"):
            path = ROOT / entry[key]
            if not path.is_file() or path.stat().st_size == 0:
                errors.append(f"missing or empty {entry[key]}")
        data_path = ROOT / entry["data_file"]
        if data_path.is_file() and sha256(data_path) != entry.get("data_sha256"):
            errors.append(f"data hash mismatch for {entry['figure_id']}")
        png_path = ROOT / entry["png_path"]
        if png_path.is_file():
            try:
                with Image.open(png_path) as image:
                    if image.width < 1000 or image.height < 700:
                        errors.append(f"PNG resolution too small for {entry['figure_id']}: {image.size}")
                    if image.format != "PNG":
                        errors.append(f"not a PNG: {entry['png_path']}")
            except Exception as exc:
                errors.append(f"cannot read PNG {entry['png_path']}: {exc}")

    with gzip.open(FREEZE_REFERENCE, "rb") as stream:
        payload = pickle.load(stream)
    times = np.asarray(payload["times_s"], dtype=float)
    nodes = np.asarray(payload["grid"]["nodes_m"], dtype=float)
    temperature = np.asarray(payload["temperatures_k"], dtype=float) - 273.15
    moisture = np.asarray(payload["moistures_kg_kg"], dtype=float)
    for name, array in (("temperature", temperature), ("moisture", moisture)):
        if not np.isfinite(array).all():
            errors.append(f"{name} figure source contains NaN/Inf")

    paper_count = 0
    paper_pass = 0
    workbook = openpyxl.load_workbook(FINAL_RESULT, read_only=True, data_only=False)
    try:
        for sheet_name, field in (("温度", temperature), ("水分浓度", moisture)):
            sheet = workbook[sheet_name]
            for time_s in PAPER_TIMES_S:
                time_index = _time_index(times, time_s)
                for position_cm in PAPER_POSITIONS_CM:
                    paper_count += 1
                    position_index = _position_index(nodes, position_cm)
                    raw_value = float(field[time_index, position_index])
                    expected = rounded(raw_value)
                    actual = Decimal(str(sheet.cell(row=time_s + 1, column=2 + int(round(position_cm * 10))).value))
                    if actual == expected:
                        paper_pass += 1
                    else:
                        errors.append(f"paper trace mismatch: {sheet_name} t={time_s} r={position_cm}")
    finally:
        workbook.close()

    rng = random.Random(20260911)
    csv_entries = [entry for entry in figure_entries if entry["figure_id"] in {"FIG-Q1-01", "FIG-Q1-02", "FIG-Q1-05", "FIG-Q1-06"}]
    csv_records: list[dict[str, str]] = []
    for entry in csv_entries:
        with (ROOT / entry["data_file"]).open(encoding="utf-8", newline="") as stream:
            csv_records.extend(csv.DictReader(stream))
    sample = rng.sample(csv_records, 20)
    random_pass = 0
    for record in sample:
        field = temperature if "temperature" in record["figure_id"].lower() else moisture
        time_index = _time_index(times, float(record["time_s"]))
        position_index = _position_index(nodes, float(record["distance_cm"]))
        expected = float(field[time_index, position_index])
        if "temperature" in record["figure_id"].lower():
            expected -= 273.15
        if abs(expected - float(record["temperature_c"] if "temperature_c" in record else record["moisture_kg_kg"])) <= 1.0e-12:
            random_pass += 1
        else:
            errors.append(f"random figure-data mismatch: {record}")

    for entry in figure_entries:
        if entry["figure_id"] not in {"FIG-Q1-03", "FIG-Q1-04"}:
            continue
        with np.load(ROOT / entry["data_file"]) as data:
            if tuple(data["values"].shape) != (7201, 339):
                errors.append(f"heatmap shape mismatch: {entry['figure_id']}")
            if not np.isfinite(data["values"]).all():
                errors.append(f"heatmap contains NaN/Inf: {entry['figure_id']}")

    checks = {
        "all_required_figures_present": actual_ids == required_ids,
        "all_assets_nonempty": not any("missing or empty" in error for error in errors),
        "all_pngs_300dpi_scale": not any("resolution too small" in error for error in errors),
        "source_hash_protected": source_hash == EXPECTED_FREEZE_HASH and manifest.get("source_hash") == EXPECTED_FREEZE_HASH,
        "paper_official_points": paper_pass == paper_count == 70,
        "random_figure_data_points": random_pass == 20,
    }
    return {
        "status": "PASS" if not errors and all(checks.values()) else "FAIL",
        "checks": checks,
        "paper_official_point_spot_check": {"count": paper_count, "pass_count": paper_pass},
        "random_figure_data_spot_check": {"seed": 20260911, "count": 20, "pass_count": random_pass},
        "errors": errors,
    }


def main() -> int:
    report = validate()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
