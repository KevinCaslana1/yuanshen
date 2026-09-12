"""Materialize raw signed/absolute comparison tables from completed audits."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            f"{float(row['time_s']):.12g}|{float(row['radius_cm']):.12g}": row
            for row in csv.DictReader(handle)
        }


def write_pair(path: Path, left_path: Path, right_path: Path) -> None:
    left, right = load(left_path), load(right_path)
    rows = []
    for key in sorted(set(left) & set(right), key=lambda value: tuple(float(part) for part in value.split("|"))):
        a, b = left[key], right[key]
        signed_t = float(a["temperature_C"]) - float(b["temperature_C"])
        signed_c = float(a["moisture_kg_kg"]) - float(b["moisture_kg_kg"])
        rows.append({
            "time_s": float(a["time_s"]),
            "radius_cm": float(a["radius_cm"]),
            "temperature_ref_C": float(b["temperature_C"]),
            "temperature_test_C": float(a["temperature_C"]),
            "temperature_signed_error_C": signed_t,
            "temperature_absolute_error_C": abs(signed_t),
            "moisture_ref_kg_kg": float(b["moisture_kg_kg"]),
            "moisture_test_kg_kg": float(a["moisture_kg_kg"]),
            "moisture_signed_error_kg_kg": signed_c,
            "moisture_absolute_error_kg_kg": abs(signed_c),
        })
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    transition = ROOT / "experiments" / "EXP-Q2-ACC-T-FORMAL"
    early = ROOT / "experiments" / "EXP-Q2-ACC-C-FORMAL"
    write_pair(
        transition / "comparison.csv",
        transition / "candidate_dt0.25_n320_cluster3" / "snapshots.csv",
        transition / "reference_dt0.125_n320_cluster3" / "snapshots.csv",
    )
    write_pair(
        early / "comparison.csv",
        early / "candidate_dt0.25_n320_cluster3_early5" / "snapshots.csv",
        early / "reference_policy_dt0.125_n640_cluster2_early5" / "snapshots.csv",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
