"""Materialize CSV/Markdown mirrors for the Q3/Q4 candidate tables."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def markdown_from_csv(source: Path, destination: Path) -> None:
    with source.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    header = rows[0]
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows[1:])
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    candidate_tables = ROOT / "deliverables" / "candidate" / "tables"
    paper_tables = ROOT / "deliverables" / "candidate" / "paper" / "tables"
    for question, source_name, candidate_stem, paper_stem in (
        ("Q3", "table5.csv", "q3_table5", "table5_q3"),
        ("Q4", "table6.csv", "q4_table6", "table6_q4"),
    ):
        source = ROOT / "experiments" / f"{question}_PRODUCTION" / source_name
        for directory, stem in ((candidate_tables, candidate_stem), (paper_tables, paper_stem)):
            shutil.copyfile(source, directory / f"{stem}.csv")
            markdown_from_csv(source, directory / f"{stem}.md")
        # A top-level paper CSV/Markdown mirror is convenient for manuscript
        # tooling and is part of the unified candidate package.
        top = ROOT / "deliverables" / "candidate" / "paper"
        shutil.copyfile(source, top / f"{paper_stem}.csv")
        markdown_from_csv(source, top / f"{paper_stem}.md")


if __name__ == "__main__":
    main()

