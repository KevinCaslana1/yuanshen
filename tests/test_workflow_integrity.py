import re
from pathlib import Path

from src.common.paths import CANDIDATE_ROOT, FINAL_ROOT, OFFICIAL_ROOT, assert_deliverable_output, assert_not_official_output


ROOT = Path(__file__).resolve().parents[1]


def test_q4_and_pre_modeling_files_exist() -> None:
    assert (ROOT / "src" / "q4").is_dir()
    assert (ROOT / "docs" / "DELIVERABLE_SPEC.md").is_file()
    assert (ROOT / "config" / "deliverables.json").is_file()


def test_candidate_and_final_are_empty_of_workbooks() -> None:
    for root in (CANDIDATE_ROOT, FINAL_ROOT):
        assert root.is_dir()
        assert not list(root.glob("*.xlsx"))
        assert not list(root.glob("*.xls"))


def test_path_guard_rejects_official_source() -> None:
    official_file = OFFICIAL_ROOT / "附件" / "附件3" / "result1.xlsx"
    try:
        assert_not_official_output(official_file)
    except ValueError:
        pass
    else:
        raise AssertionError("official source path was not rejected")

    assert assert_deliverable_output(CANDIDATE_ROOT / "result1.xlsx") == CANDIDATE_ROOT / "result1.xlsx"
    assert assert_deliverable_output(FINAL_ROOT / "result1.xlsx") == FINAL_ROOT / "result1.xlsx"


def test_no_formal_evidence_records_exist() -> None:
    experiments = (ROOT / "docs" / "EXPERIMENTS.md").read_text(encoding="utf-8")
    findings = (ROOT / "docs" / "FINDINGS.md").read_text(encoding="utf-8")
    claims = (ROOT / "docs" / "CLAIMS.md").read_text(encoding="utf-8")
    assert not re.search(r"EXP-\d{3}", experiments)
    assert not re.search(r"FIND-\d{3}", findings)
    assert not re.search(r"C-\d{3}", claims)


def test_state_remains_pre_modeling() -> None:
    state = (ROOT / "docs" / "STATE.md").read_text(encoding="utf-8")
    assert "PRE-MODELING READY" in state
    assert "PRE-MODELING GATE PASS" in state
    assert "Q1 | NOT STARTED" in state
    assert "Q2 | NOT STARTED" in state
    assert "Q3 | NOT STARTED" in state
    assert "Q4 | NOT STARTED" in state
    assert "NONE" in state
