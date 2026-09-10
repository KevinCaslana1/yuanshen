import re
from pathlib import Path

from src.common.paths import CANDIDATE_ROOT, FINAL_ROOT, OFFICIAL_ROOT, assert_deliverable_output, assert_not_official_output


ROOT = Path(__file__).resolve().parents[1]


def test_q1_design_and_pre_modeling_files_exist() -> None:
    assert (ROOT / "src" / "q4").is_dir()
    assert (ROOT / "docs" / "Q1_PLAN.md").is_file()
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
    assert re.search(r"EXP-001", experiments)
    assert re.search(r"EXP-007", experiments)
    assert not re.search(r"\| (RUNNING|COMPLETED|FAILED|ABANDONED) \|", experiments)
    assert not re.search(r"FIND-\d{3}", findings)
    assert not re.search(r"C-\d{3}", claims)
    assert not list((ROOT / "experiments").glob("EXP-*/"))


def test_state_waits_for_q1_implementation_authorization() -> None:
    state = (ROOT / "docs" / "STATE.md").read_text(encoding="utf-8")
    assert "Q1 MODEL DESIGN" in state
    assert "Q1 | MODEL DESIGN COMPLETE / WAITING IMPLEMENTATION APPROVAL" in state
    assert "Q2 | NOT STARTED" in state
    assert "Q3 | NOT STARTED" in state
    assert "Q4 | NOT STARTED" in state
    assert "不得自动运行正式求解或生成 result1.xlsx" in state
