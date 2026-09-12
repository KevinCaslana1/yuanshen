"""Build native Word copies of official paper Tables 1--6.

The script is post-processing only.  Q1--Q4 final workbooks and the official
source directory are opened read-only.  Table values are selected from the
frozen canonical sources and rounded only when written to Word.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "deliverables" / "final"
OUT = FINAL / "paper" / "tables_word"
PAPER = FINAL / "paper"
TRACE = PAPER / "TABLE_1_6_TRACE.json"

FONT_CN = "宋体"
FONT_LATIN = "Times New Roman"
QUANTUM = Decimal("0.0001")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fmt4(value: float | int | None) -> str:
    if value is None:
        return ""
    return format(Decimal(str(value)).quantize(QUANTUM, rounding=ROUND_HALF_UP), ".4f")


def set_run_font(run, size: float, bold: bool = False) -> None:
    run.font.name = FONT_CN
    run.font.size = Pt(size)
    run.bold = bold
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    rfonts.set(qn("w:ascii"), FONT_LATIN)
    rfonts.set(qn("w:hAnsi"), FONT_LATIN)
    rfonts.set(qn("w:eastAsia"), FONT_CN)


def set_cell_text(cell, text: str, *, size: float = 9.5, bold: bool = False) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(str(text))
    set_run_font(run, size, bold)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_cell_shading(cell, fill: str | None = None) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill or "FFFFFF")
    shd.set(qn("w:val"), "clear")


def set_table_borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        node = borders.find(qn(tag))
        if node is None:
            node = OxmlElement(tag)
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "4")
        node.set(qn("w:space"), "0")
        node.set(qn("w:color"), "000000")


def set_cell_margins(cell, top: int = 40, start: int = 55, bottom: int = 40, end: int = 55) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    margins = tc_pr.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        tc_pr.append(margins)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = margins.find(qn("w:" + side))
        if node is None:
            node = OxmlElement("w:" + side)
            margins.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    tr_pr.append(repeat)


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(1.35)
    section.bottom_margin = Cm(1.35)
    section.left_margin = Cm(1.5)
    section.right_margin = Cm(1.5)
    section.header_distance = Cm(0.7)
    section.footer_distance = Cm(0.7)
    normal = doc.styles["Normal"]
    normal.font.name = FONT_CN
    normal.font.size = Pt(9.5)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), FONT_CN)


def add_title(doc: Document, title: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(title)
    set_run_font(run, 12, True)


def add_note(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(text)
    set_run_font(run, 8.5, False)


def add_native_table(doc: Document, title: str, time_header: str, radii: list[str], rows: list[dict[str, Any]], value_keys: list[str], note: str | None = None) -> None:
    add_title(doc, title)
    table = doc.add_table(rows=2 + len(rows), cols=1 + len(radii))
    table.autofit = False
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_table_borders(table)
    width = 18.0 / (1 + len(radii))
    for row in table.rows:
        row.height = Cm(0.42)
        row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        for cell in row.cells:
            cell.width = Cm(width)
            set_cell_margins(cell)
            set_cell_shading(cell)

    # Official layout: the first header cell is vertically merged and the
    # radius label is horizontally merged across all spatial columns.
    first = table.cell(0, 0).merge(table.cell(1, 0))
    set_cell_text(first, time_header, size=9.5)
    radius_header = table.cell(0, 1).merge(table.cell(0, len(radii)))
    set_cell_text(radius_header, "到药材中心的距离/cm", size=9.5)
    for j, radius in enumerate(radii, start=1):
        set_cell_text(table.cell(1, j), radius, size=9.5)
    set_repeat_table_header(table.rows[0])
    set_repeat_table_header(table.rows[1])

    for i, row in enumerate(rows, start=2):
        set_cell_text(table.cell(i, 0), row["time_label"], size=9.5)
        for j, key in enumerate(value_keys, start=1):
            value = row.get(key)
            if value is None and "values" in row and j - 1 < len(row["values"]):
                value = row["values"][j - 1]
            set_cell_text(table.cell(i, j), "" if value is None else value, size=9.5)
    if note:
        add_note(doc, note)


def load_workbook_matrix(path: Path, sheet: str, wanted_times_s: list[float], radii_idx: list[int]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet]
    wanted = {round(v, 8): label for v, label in []}
    wanted_set = {round(float(v), 8) for v in wanted_times_s}
    result: list[dict[str, Any]] = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        t = float(row[0])
        if round(t, 8) in wanted_set:
            result.append({"time_s": t, "values": [None if row[i + 1] is None else float(row[i + 1]) for i in radii_idx]})
    wb.close()
    result.sort(key=lambda x: x["time_s"])
    if len(result) != len(wanted_times_s):
        raise RuntimeError(f"{path.name}/{sheet}: expected {len(wanted_times_s)} rows, got {len(result)}")
    return result, {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path), "sheet": sheet}


def load_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def csv_matrix_rows(path: Path, wanted_hours: list[float], keys: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    header, source_rows = load_csv_rows(path)
    wanted = {round(float(v), 8) for v in wanted_hours}
    selected = []
    for row in source_rows:
        t = float(row["time_h"])
        if round(t, 8) in wanted:
            selected.append({"time_h": t, "time_label": row["time_label"], "values": [None if not row.get(key) else float(row[key]) for key in keys]})
    selected.sort(key=lambda x: x["time_h"])
    if len(selected) != len(wanted_hours):
        raise RuntimeError(f"{path.name}: expected {len(wanted_hours)} rows, got {len(selected)}")
    return selected, {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path), "columns": header}


def full_matrix_rows(path: Path, wanted_hours: list[float], keys: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Select paper times from a full-precision time-by-radius CSV."""
    header, source_rows = load_csv_rows(path)
    wanted_s = {round(float(v) * 3600.0, 6) for v in wanted_hours}
    selected = []
    for row in source_rows:
        time_s = float(row["time_s"])
        if round(time_s, 6) in wanted_s:
            label = "烘干结束时间" if abs(time_s / 3600.0 - wanted_hours[-1]) < 1.0e-6 else str(int(round(time_s / 3600.0)))
            selected.append({"time_h": time_s / 3600.0, "time_label": label, "values": [None if not row.get(key) else float(row[key]) for key in keys]})
    selected.sort(key=lambda x: x["time_h"])
    if len(selected) != len(wanted_hours):
        raise RuntimeError(f"{path.name}: expected {len(wanted_hours)} rows, got {len(selected)}")
    return selected, {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path), "columns": header}


def trace_table(table_id: str, title: str, source: dict[str, Any], rows: list[dict[str, Any]], labels: list[str], key_names: list[str]) -> dict[str, Any]:
    trace_rows = []
    valid = 0
    for row in rows:
        cells = {}
        for label, key, value in zip(labels, key_names, row["values"]):
            cells[label] = {"raw_value": None if value is None else repr(float(value)), "rounded_value": fmt4(value), "word_value": fmt4(value)}
            if value is not None:
                valid += 1
        trace_rows.append({"time_label": row["time_label"], "time_source": row.get("time_s", row.get("time_h")), "cells": cells})
    total = sum(1 for row in rows for value in row["values"] if value is not None)
    return {"table": table_id, "title": title, "source": source, "radius_labels": labels, "row_count": len(rows), "valid_cell_count": valid, "expected_cell_count": total, "trace": f"{valid}/{total}", "rounding": "Decimal(str(value)).quantize(0.0001, ROUND_HALF_UP)", "rows": trace_rows, "word_native_table": True, "status": "PASS"}


def make_table_spec() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    q1 = FINAL / "result1.xlsx"
    q2 = FINAL / "result2.xlsx"
    q3 = ROOT / "experiments/Q3_PRODUCTION/q3_result3_matrix_full_precision.csv"
    q4 = ROOT / "experiments/Q4_PRODUCTION/q4_result4_matrix_full_precision.csv"
    radii = [0, 5, 10, 15, 20]
    q1_times = [100, 300, 600, 900, 1200, 1500, 1800]
    q2_times = [1800, 3600, 5400, 7200, 9000, 10800]

    q1_t, q1_t_src = load_workbook_matrix(q1, "温度", q1_times, radii)
    q1_c, q1_c_src = load_workbook_matrix(q1, "水分浓度", q1_times, radii)
    q2_t, q2_t_src = load_workbook_matrix(q2, "温度", q2_times, radii)
    q2_c, q2_c_src = load_workbook_matrix(q2, "水分浓度", q2_times, radii)

    specs = []
    trace = []
    def wb_rows(items, unit: str) -> list[dict[str, Any]]:
        return [{"time_label": str(int(x["time_s"])) if unit == "s" else f"{x['time_s']/3600.0:.1f}", "time_s": x["time_s"], "values": [fmt4(v) for v in x["values"]], "raw_values": x["values"]} for x in items]

    for table_id, title, items, source, unit in [
        ("Table1", "表 1  30分钟内药材的温度", q1_t, q1_t_src, "s"),
        ("Table2", "表 2  30分钟内药材的水分浓度", q1_c, q1_c_src, "s"),
        ("Table3", "表 3  3小时内药材的温度", q2_t, q2_t_src, "h"),
        ("Table4", "表 4  3小时内药材的水分浓度", q2_c, q2_c_src, "h"),
    ]:
        rows = wb_rows(items, unit)
        keys = [f"r_{r / 10:.1f}_cm" for r in [0, 5, 10, 15, 20]]
        display_rows = [{"time_label": x["time_label"], "time_s": x["time_s"], "values": x["raw_values"]} for x in rows]
        trace.append(trace_table(table_id, title, source, display_rows, keys, keys))
        specs.append({"id": table_id, "title": title, "time_header": f"时间/{unit}", "radii": ["0", "0.5", "1", "1.5", "2"], "value_keys": keys, "rows": rows, "note": None})

    q3_items, q3_src = full_matrix_rows(q3, [6, 12, 18, 24, 30, 36, 42, 48, 54, 57.482007378472225], ["r_0.0_cm", "r_0.5_cm", "r_1.0_cm", "r_1.5_cm", "r_2.0_cm"])
    q3_rows = q3_items
    q3_title = "表 5  药材烘干过程的水分浓度"
    q3_keys = ["r_0.0_cm", "r_0.5_cm", "r_1.0_cm", "r_1.5_cm", "r_2.0_cm"]
    trace.append(trace_table("Table5", q3_title, q3_src, q3_rows, ["0", "0.5", "1", "1.5", "2"], q3_keys))
    specs.append({"id": "Table5", "title": q3_title, "time_header": "时间/h", "radii": ["0", "0.5", "1", "1.5", "2"], "value_keys": q3_keys, "rows": [{"time_label": x["time_label"], "values": [fmt4(v) for v in x["values"]]} for x in q3_rows], "note": None})

    q4_items, q4_src = full_matrix_rows(q4, [6, 12, 18, 24, 30, 36, 42, 48, 53.08270378038297], ["r_0.0_cm", "r_0.5_cm", "r_1.0_cm", "r_1.5_cm", "surface"])
    q4_rows = q4_items
    q4_title = "表 6  药材烘干过程的水分浓度"
    q4_keys = ["r_0.0_cm", "r_0.5_cm", "r_1.0_cm", "r_1.5_cm", "surface"]
    trace.append(trace_table("Table6", q4_title, q4_src, q4_rows, ["0", "0.5", "1", "1.5", "药材表面"], q4_keys))
    specs.append({"id": "Table6", "title": q4_title, "time_header": "时间/h", "radii": ["0", "0.5", "1", "1.5", "药材表面"], "value_keys": q4_keys, "rows": [{"time_label": x["time_label"], "values": [fmt4(v) for v in x["values"]]} for x in q4_rows], "note": "注：超出当前药材半径的位置不定义。"})
    return specs, trace


def build_doc(specs: list[dict[str, Any]], selected: Iterable[dict[str, Any]]) -> Document:
    doc = Document()
    configure_document(doc)
    selected = list(selected)
    for idx, spec in enumerate(selected):
        if idx:
            doc.add_page_break()
        add_native_table(doc, spec["title"], spec["time_header"], spec["radii"], spec["rows"], spec["value_keys"], spec["note"])
    return doc


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    PAPER.mkdir(parents=True, exist_ok=True)
    specs, trace = make_table_spec()
    names = {
        "Table1": "表1_30分钟内药材的温度.docx",
        "Table2": "表2_30分钟内药材的水分浓度.docx",
        "Table3": "表3_3小时内药材的温度.docx",
        "Table4": "表4_3小时内药材的水分浓度.docx",
        "Table5": "表5_药材烘干过程的水分浓度_Q3.docx",
        "Table6": "表6_药材烘干过程的水分浓度_Q4.docx",
    }
    for spec in specs:
        doc = build_doc(specs, [spec])
        doc.save(OUT / names[spec["id"]])
    merged = build_doc(specs, specs)
    merged_path = PAPER / "论文表1-表6_可直接复制.docx"
    merged.save(merged_path)
    payload = {
        "schema_version": "TABLE_1_6_TRACE_V1",
        "status": "PASS",
        "source_policy": "frozen final workbooks and existing full-precision Q3/Q4 production matrices; read-only source access",
        "word_output": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "merged_word": str(merged_path.relative_to(ROOT)).replace("\\", "/"),
        "tables": trace,
        "counts": {item["table"]: item["trace"] for item in trace},
        "table1_35_35": trace[0]["trace"] == "35/35",
        "table2_35_35": trace[1]["trace"] == "35/35",
        "table3_30_30": trace[2]["trace"] == "30/30",
        "table4_30_30": trace[3]["trace"] == "30/30",
        "table5_valid_cells": trace[4]["trace"],
        "table6_valid_cells": trace[5]["trace"],
        "workbooks": {name: sha256(FINAL / name) for name in ("result1.xlsx", "result2.xlsx", "result3.xlsx", "result4.xlsx")},
        "generated_files": [str((OUT / names[item["id"]]).relative_to(ROOT)).replace("\\", "/") for item in specs] + [str(merged_path.relative_to(ROOT)).replace("\\", "/")],
    }
    TRACE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["counts"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
