"""Validate the machine-readable deliverable contract without generating results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

try:
    import openpyxl
except ImportError as exc:  # pragma: no cover - environment failure
    raise SystemExit("openpyxl is required for deliverable-contract validation") from exc


REQUIRED_GLOBAL_KEYS = {
    "schema_version",
    "contract_status",
    "official_source_root",
    "candidate_root",
    "final_root",
    "precision_decimals",
    "shape_policy",
    "deliverables",
}
REQUIRED_SHEET_KEYS = {
    "name",
    "time_unit",
    "time_sampling",
    "space_unit",
    "space_sampling",
    "value_unit",
    "decimal_precision",
    "skeleton_shape",
    "expected_final_shape",
    "required_cells",
    "forbidden_changes",
    "validation_status",
    "open_questions",
}


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_contract(root: Path) -> list[str]:
    errors: list[str] = []
    config_path = root / "config" / "deliverables.json"
    spec_path = root / "docs" / "DELIVERABLE_SPEC.md"
    if not config_path.is_file():
        return ["missing config/deliverables.json"]
    if not spec_path.is_file():
        return ["missing docs/DELIVERABLE_SPEC.md"]

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"invalid JSON: {exc}"]
    spec_text = spec_path.read_text(encoding="utf-8")

    missing_globals = REQUIRED_GLOBAL_KEYS - set(config)
    errors.extend(f"missing global key: {key}" for key in sorted(missing_globals))
    if config.get("contract_status") == "VERIFIED":
        errors.append("contract cannot be VERIFIED while open questions remain")
    if config.get("shape_policy") != "TEMPLATE_SKELETON_IS_NOT_FINAL_OUTPUT_DIMENSION":
        errors.append("shape policy must distinguish TEMPLATE_SKELETON from final shape")
    if config.get("precision_decimals") != 4:
        errors.append("precision_decimals must be 4")

    official_root = (root / config.get("official_source_root", "A题")).resolve()
    candidate_root = (root / config.get("candidate_root", "deliverables/candidate")).resolve()
    final_root = (root / config.get("final_root", "deliverables/final")).resolve()
    deliverables = config.get("deliverables", [])
    if {item.get("question") for item in deliverables} != {"Q1", "Q2", "Q3", "Q4"}:
        errors.append("deliverables must contain exactly Q1, Q2, Q3, and Q4")

    for item in deliverables:
        for key in ("question", "file", "official_template", "candidate_path", "final_path", "sheets"):
            if key not in item:
                errors.append(f"{item.get('question', '<unknown>')} missing key: {key}")
        official_template = root / item.get("official_template", "")
        if not official_template.is_file():
            errors.append(f"missing official template: {item.get('official_template')}")
        else:
            workbook = openpyxl.load_workbook(official_template, read_only=True, data_only=False)
            actual_sheets = tuple(workbook.sheetnames)
            workbook.close()
            expected_sheets = tuple(sheet.get("name") for sheet in item.get("sheets", []))
            if actual_sheets != expected_sheets:
                errors.append(f"sheet mismatch {item.get('file')}: expected={expected_sheets} actual={actual_sheets}")

        candidate = (root / item.get("candidate_path", "")).resolve()
        final = (root / item.get("final_path", "")).resolve()
        if not _within(candidate, candidate_root):
            errors.append(f"candidate path escapes candidate root: {item.get('candidate_path')}")
        if not _within(final, final_root):
            errors.append(f"final path escapes final root: {item.get('final_path')}")
        if _within(candidate, official_root) or _within(final, official_root):
            errors.append(f"deliverable path overlaps official source: {item.get('file')}")

        section_marker = f"## {item.get('file')}"
        start = spec_text.find(section_marker)
        if start < 0:
            errors.append(f"missing Markdown section: {section_marker}")
            section = ""
        else:
            next_section = spec_text.find("\n## ", start + len(section_marker))
            section = spec_text[start:] if next_section < 0 else spec_text[start:next_section]
        for label in ("Official Template", "Candidate Path", "Final Path", "Sheet Name", "Time Header", "Time Unit", "Time Sampling Rule", "Spatial Header", "Spatial Unit", "Spatial Sampling Rule", "Value Unit", "Decimal Precision", "Skeleton Shape", "Expected Final Shape", "Expansion Rule", "Required Cells", "Forbidden Changes", "Validation Status", "Open Questions"):
            if f"- {label}:" not in section:
                errors.append(f"{item.get('file')} missing Markdown field: {label}")
        for value in (item.get("official_template"), item.get("candidate_path"), item.get("final_path")):
            if value not in section:
                errors.append(f"{item.get('file')} Markdown path mismatch: {value}")

        for sheet in item.get("sheets", []):
            missing_sheet_keys = REQUIRED_SHEET_KEYS - set(sheet)
            errors.extend(f"{item.get('file')}/{sheet.get('name')} missing key: {key}" for key in sorted(missing_sheet_keys))
            if sheet.get("validation_status") == "VERIFIED" and sheet.get("open_questions"):
                errors.append(f"open questions incorrectly marked VERIFIED: {item.get('file')}/{sheet.get('name')}")
            if sheet.get("expected_final_shape", {}).get("status") == "TEMPLATE_SKELETON":
                errors.append(f"skeleton shape incorrectly used as final shape: {item.get('file')}/{sheet.get('name')}")
            if sheet.get("decimal_precision") != config.get("precision_decimals"):
                errors.append(f"precision mismatch: {item.get('file')}/{sheet.get('name')}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate_contract(args.root.resolve())
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        print(f"Deliverable contract validation failed: {len(errors)} issue(s)")
        return 1
    print("[PASS] config/deliverables.json and docs/DELIVERABLE_SPEC.md are consistent")
    print("[PASS] Q1-Q4 paths, sheets, units, precision, skeleton/final policies, and open-question states validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
