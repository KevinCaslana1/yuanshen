"""Build the candidate Word Table 1--6 package with Q4 Table6 from L.

Tables 1--5 are read from their already frozen sources.  This wrapper changes
only the post-processing destinations and Q4 source used by the existing
table generator; it never runs a numerical solver.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.generate_paper_tables_word as generator


def main() -> None:
    candidate = ROOT / "deliverables" / "candidate_reaudit"
    paper = candidate / "paper"
    generator.FINAL = ROOT / "deliverables" / "final"
    generator.OUT = paper / "tables_word"
    generator.PAPER = paper
    generator.TRACE = paper / "TABLE_1_6_TRACE.json"
    generator.Q4_MATRIX_SOURCE = ROOT / "experiments" / "Q4_PAPER_FINAL_N768" / "official_samples_with_endpoint_raw.csv"
    event = json.loads((ROOT / "experiments" / "Q4_PAPER_FINAL_N768" / "event.json").read_text(encoding="utf-8"))
    generator.Q4_EVENT_HOURS = float(event["t4_h"])
    generator.main()


if __name__ == "__main__":
    main()
