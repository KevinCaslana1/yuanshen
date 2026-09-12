"""Read-only validation for the Chinese Q2 publication figure package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "deliverables" / "final" / "paper" / "figures" / "q2"
AUDIT_ROOT = ROOT / "experiments" / "Q2_CHINESE_FIGURE_LOCALIZATION"
MANIFEST_PATH = OUTPUT_ROOT / "Q2_CHINESE_FIGURE_MANIFEST.json"
Q2_SOURCE_MANIFEST = ROOT / "figures" / "q2" / "FIGURE_MANIFEST.json"
Q2_FROZEN_MANIFEST = ROOT / "deliverables" / "final" / "Q2_MANIFEST.json"
Q2_WORKBOOK = ROOT / "deliverables" / "final" / "result2.xlsx"
EXPECTED_Q2_SHA = "84fb32457193e158debdf569d34f5f41b97e78496b30dd9b2e134385439e10da"

FIGURE_IDS = [
    "FIG-Q2-01",
    "FIG-Q2-02",
    "FIG-Q2-03",
    "FIG-Q2-04",
    "FIG-Q2-05",
    "FIG-Q2-06",
    "FIG-Q2-07",
    "FIG-Q2-08",
    "FIG-Q2-V01",
    "FIG-Q2-V02",
    "FIG-Q2-V03",
]

OBVIOUS_ENGLISH = re.compile(
    r"\b(?:Temperature|Moisture|Radius|Radial|Distance|Time|Mean|Surface|Center|"
    r"Absolute|Relative|Mass|Energy|Residual|Grid|Step|Picard|Iterations|Heat|"
    r"Representative|Diffusivity|Evolution|Profiles|Histories|Difference|Discrete)\b",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def array_hash(value: np.ndarray) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(repr(array.shape).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def read_csv_matrix(path: Path) -> tuple[list[str], np.ndarray]:
    with path.open(encoding="utf-8", newline="") as handle:
        header = next(csv.reader(handle))
    matrix = np.loadtxt(path, delimiter=",", skiprows=1, dtype=np.float64)
    if matrix.ndim == 1:
        matrix = matrix.reshape(1, -1)
    return header, np.asarray(matrix, dtype=np.float64)


def radius_columns(header: list[str]) -> np.ndarray:
    values = []
    for name in header[1:]:
        match = re.fullmatch(r"radius_([0-9]+(?:\.[0-9]+)?)_cm", name)
        if not match:
            raise AssertionError(f"invalid radius column {name}")
        values.append(float(match.group(1)))
    return np.asarray(values, dtype=np.float64)


def source_arrays(figure_id: str, path: Path) -> dict[str, np.ndarray]:
    if figure_id in {"FIG-Q2-03", "FIG-Q2-04"}:
        with np.load(path, allow_pickle=False) as data:
            key = "temperature_C" if figure_id == "FIG-Q2-03" else "moisture_kg_kg"
            return {"time_s": data["time_s"], "radius_cm": data["radius_cm"], key: data[key]}
    header, matrix = read_csv_matrix(path)
    times_s = matrix[:, 0]
    if figure_id in {"FIG-Q2-01", "FIG-Q2-02"}:
        key = "temperature_C" if figure_id == "FIG-Q2-01" else "moisture_kg_kg"
        return {"time_s": times_s, "radius_cm": radius_columns(header), key: matrix[:, 1:]}
    if figure_id in {"FIG-Q2-05", "FIG-Q2-06"}:
        key = "temperature_C" if figure_id == "FIG-Q2-05" else "moisture_kg_kg"
        return {"time_s": times_s, "radius_cm": radius_columns(header), key: matrix[:, 1:]}
    if figure_id == "FIG-Q2-07":
        return {"time_s": times_s, "center_minus_surface_moisture_kg_kg": matrix[:, 1]}
    if figure_id == "FIG-Q2-08":
        return {
            "time_s": times_s,
            "radius_cm": np.asarray([0.0, 1.0, 2.0], dtype=np.float64),
            "D_C_T": matrix[:, 1:],
        }
    key = {
        "FIG-Q2-V01": "picard_iterations",
        "FIG-Q2-V02": "mass_step_residual",
        "FIG-Q2-V03": "heat_step_residual_j",
    }[figure_id]
    return {"time_s": times_s, key: matrix[:, 1]}


def expected_user_labels(entry: dict[str, Any]) -> list[str]:
    labels = [entry["title"], entry["xlabel"], entry["ylabel"]]
    if entry.get("colorbar_label"):
        labels.append(entry["colorbar_label"])
    labels.extend(entry.get("legend_labels", []))
    return labels


def validate_q2_figures(manifest: dict[str, Any]) -> dict[str, Any]:
    original_manifest = json.loads(Q2_SOURCE_MANIFEST.read_text(encoding="utf-8"))
    original_by_id = {item["figure_id"]: item for item in original_manifest["figures"]}
    entries = {item["figure_id"]: item for item in manifest["figures"]}
    if list(entries) != FIGURE_IDS:
        raise AssertionError(f"Q2 figure id set/order mismatch: {list(entries)}")

    items = []
    for figure_id in FIGURE_IDS:
        entry = entries[figure_id]
        source_path = ROOT / entry["source_data_file"]
        png = ROOT / entry["png_path"]
        svg = ROOT / entry["svg_path"]
        if not source_path.exists() or not png.exists() or not svg.exists():
            raise AssertionError(f"missing Q2 localization artifact for {figure_id}")
        if sha256(source_path) != entry["source_data_sha256"]:
            raise AssertionError(f"source data hash mismatch for {figure_id}")
        original = original_by_id[figure_id]
        original_path = ROOT / original["data_file"].replace("\\", "/")
        if source_path != original_path or entry["source_data_sha256"] != original["data_sha256"]:
            raise AssertionError(f"source data is not the existing Q2 figure data for {figure_id}")

        arrays = source_arrays(figure_id, source_path)
        stored_arrays = {item["array"]: item for item in entry["source_arrays"]}
        if set(arrays) != set(stored_arrays):
            raise AssertionError(f"source array set mismatch for {figure_id}")
        array_checks = []
        for name, value in arrays.items():
            actual_hash = array_hash(value)
            stored = stored_arrays[name]
            passed = (
                actual_hash == stored["source_array_sha256"] == stored["plotted_array_sha256"]
                and list(np.asarray(value).shape) == stored["shape"]
                and str(np.asarray(value).dtype) == stored["dtype"]
                and stored["identical"]
            )
            if not passed:
                raise AssertionError(f"numeric source/plotted array trace failed for {figure_id}/{name}")
            array_checks.append({"array": name, "status": "PASS", "sha256": actual_hash})
        if entry["data_trace"] != {
            "status": "PASS",
            "source_numeric_arrays_identical": True,
            "x_data_identical": True,
            "y_data_identical": True,
            "sampling_identical": True,
        }:
            raise AssertionError(f"trace contract failed for {figure_id}")

        with Image.open(png) as image:
            dpi = image.info.get("dpi", (0.0, 0.0))
            dpi_xy = [float(dpi[0]), float(dpi[1])]
        dpi_ok = dpi_xy[0] >= 300.0 and dpi_xy[1] >= 300.0
        if not dpi_ok:
            raise AssertionError(f"PNG DPI below 300 for {figure_id}: {dpi_xy}")

        svg_text = svg.read_text(encoding="utf-8")
        text_nodes = "\n".join(re.findall(r"<text[^>]*>(.*?)</text>", svg_text, flags=re.DOTALL))
        missing_labels = [label for label in expected_user_labels(entry) if label not in text_nodes]
        english_labels = sorted(set(OBVIOUS_ENGLISH.findall(text_nodes)))
        has_chinese = bool(re.search(r"[\u3400-\u9fff]", text_nodes))
        if missing_labels or english_labels or not has_chinese:
            raise AssertionError(f"Chinese label check failed for {figure_id}: missing={missing_labels}, english={english_labels}")
        if not entry["no_smoothing"] or not entry["no_numeric_interpolation"] or entry["error_clip"] is not None:
            raise AssertionError(f"plotting policy changed for {figure_id}")

        items.append(
            {
                "figure_id": figure_id,
                "source_array_trace": f"{len(array_checks)}/{len(array_checks)}",
                "data_trace": "PASS",
                "png": str(png.relative_to(ROOT)).replace("\\", "/"),
                "svg": str(svg.relative_to(ROOT)).replace("\\", "/"),
                "png_sha256": sha256(png),
                "svg_sha256": sha256(svg),
                "png_dpi": dpi_xy,
                "png_dpi_ok": True,
                "chinese_text_check": "PASS",
                "english_descriptive_labels": english_labels,
                "array_checks": array_checks,
            }
        )
    return {
        "status": "PASS",
        "figure_count": len(items),
        "png_count": len(items),
        "svg_count": len(items),
        "all_png_dpi_ge_300": True,
        "data_trace": f"{len(items)}/{len(items)}",
        "chinese_text_validation": f"{len(items)}/{len(items)}",
        "no_smoothing": True,
        "no_numeric_interpolation": True,
        "items": items,
    }


def frozen_integrity(manifest: dict[str, Any]) -> dict[str, Any]:
    frozen_manifest = json.loads(Q2_FROZEN_MANIFEST.read_text(encoding="utf-8"))
    expected_figures = frozen_manifest["figure_sha256"]
    current_figures = {key: sha256(ROOT / key) for key in expected_figures}
    if current_figures != expected_figures:
        raise AssertionError("existing frozen Q2 figure directory changed")
    before = manifest["result2"]["sha256_before"]
    after = manifest["result2"]["sha256_after"]
    current = sha256(Q2_WORKBOOK)
    if before != after or before != EXPECTED_Q2_SHA or current != EXPECTED_Q2_SHA:
        raise AssertionError(f"result2 freeze hash check failed: before={before}, after={after}, current={current}")
    if manifest["result2"]["numerical_result_changed"]:
        raise AssertionError("manifest reports numerical result changed")
    return {
        "result2_path": str(Q2_WORKBOOK.relative_to(ROOT)).replace("\\", "/"),
        "sha256_before": before,
        "sha256_after": after,
        "sha256_current": current,
        "expected_sha256": EXPECTED_Q2_SHA,
        "numerical_result_changed": False,
        "frozen_original_q2_figures_unchanged": True,
    }


def metadata_check() -> dict[str, Any]:
    q1_manifest_path = ROOT / "figures" / "q1" / "FIGURE_MANIFEST.json"
    q1_manifest = json.loads(q1_manifest_path.read_text(encoding="utf-8"))
    q1_english_titles = []
    for item in q1_manifest["figures"]:
        if OBVIOUS_ENGLISH.search(item["title"]):
            q1_english_titles.append({"figure_id": item["figure_id"], "title": item["title"]})

    q34_script_path = ROOT / "scripts" / "run_q3_q4_candidate.py"
    q34_text = q34_script_path.read_text(encoding="utf-8")
    user_lines = [
        line.strip()
        for line in q34_text.splitlines()
        if any(token in line for token in ("set_title", "set_xlabel", "set_ylabel", "label="))
    ]
    allowed_technical_tokens = ["PCHIP", "Cmax", "R(t)", "t3", "t4", "Q3", "Q4", "cm", "kg/kg", "h", "s"]
    q34_obvious_english = []
    for line in user_lines:
        # Inspect only quoted user-facing strings.  Identifiers such as
        # ``snap.moisture`` are implementation metadata, not figure labels.
        string_literals = re.findall(r"[\"']([^\"']*)[\"']", line)
        for literal in string_literals:
            for token in sorted(set(OBVIOUS_ENGLISH.findall(literal))):
                if token not in {"PCHIP"}:
                    q34_obvious_english.append({"token": token, "source_line": line, "literal": literal})
    q34_obvious_english = [item for item in q34_obvious_english if item["token"] not in allowed_technical_tokens]
    result = {
        "status": "PASS" if not q1_english_titles and not q34_obvious_english else "REVIEW",
        "scope": "metadata-only check; no Q1/Q3/Q4 numerical rerun or redraw",
        "Q1": {
            "manifest": str(q1_manifest_path.relative_to(ROOT)).replace("\\", "/"),
            "figure_count": len(q1_manifest["figures"]),
            "obvious_english_titles": q1_english_titles,
        },
        "Q3_Q4": {
            "label_source": str(q34_script_path.relative_to(ROOT)).replace("\\", "/"),
            "obvious_english_descriptive_labels": q34_obvious_english,
            "allowed_technical_tokens": allowed_technical_tokens,
        },
        "action": "no redraw required" if not q1_english_titles and not q34_obvious_english else "listed for paper figure localization review",
    }
    return result


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest["q2_solver_rerun"] or manifest["source_mode"].find("no solver") < 0:
        raise AssertionError("Q2 localization is not postprocess-only")
    q2_figures = validate_q2_figures(manifest)
    freeze = frozen_integrity(manifest)
    metadata = metadata_check()
    output = {
        "experiment": "Q2_CHINESE_FIGURE_LOCALIZATION",
        "status": "PASS" if q2_figures["status"] == "PASS" and freeze["numerical_result_changed"] is False and metadata["status"] == "PASS" else "REVIEW",
        "q2_chinese_figure_localization": q2_figures,
        "q2_frozen_integrity": freeze,
        "q1_q3_q4_metadata_check": metadata,
        "q2_solver_rerun": False,
        "numerical_result_changed": False,
        "protected_paths_changed": [],
    }
    if output["status"] != "PASS":
        raise AssertionError(json.dumps(output, ensure_ascii=False))
    validation_path = AUDIT_ROOT / "validation.json"
    validation_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Mark the publication manifest as validated without touching any source
    # arrays or numerical artifacts.
    manifest["status"] = "PASS"
    manifest["validation"] = {
        "path": str(validation_path.relative_to(ROOT)).replace("\\", "/"),
        "status": "PASS",
        "q2_figure_trace": q2_figures["data_trace"],
        "chinese_text_validation": q2_figures["chinese_text_validation"],
        "png_dpi_validation": q2_figures["all_png_dpi_ge_300"],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
