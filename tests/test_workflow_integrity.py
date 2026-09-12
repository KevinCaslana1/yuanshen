import re
from pathlib import Path

from src.common.paths import CANDIDATE_ROOT, FINAL_ROOT, OFFICIAL_ROOT, assert_deliverable_output, assert_not_official_output


ROOT = Path(__file__).resolve().parents[1]


def test_q1_design_and_pre_modeling_files_exist() -> None:
    assert (ROOT / "src" / "q4").is_dir()
    assert (ROOT / "docs" / "Q1_PLAN.md").is_file()
    assert (ROOT / "docs" / "DELIVERABLE_SPEC.md").is_file()
    assert (ROOT / "config" / "deliverables.json").is_file()


def test_candidate_and_final_follow_q1_approval_state() -> None:
    assert CANDIDATE_ROOT.is_dir()
    candidate_workbooks = [path for path in CANDIDATE_ROOT.glob("*.xlsx") if not path.name.startswith("~$")]
    assert all(path.name in {"result1.xlsx", "result2.xlsx", "result3.xlsx", "result4.xlsx"} for path in candidate_workbooks)
    assert (CANDIDATE_ROOT / "result1.xlsx").is_file()
    assert (CANDIDATE_ROOT / "result2.xlsx").is_file()
    assert (CANDIDATE_ROOT / "result3.xlsx").is_file()
    assert (CANDIDATE_ROOT / "result4.xlsx").is_file()
    assert not list(CANDIDATE_ROOT.glob("*.xls"))
    assert FINAL_ROOT.is_dir()
    assert (FINAL_ROOT / "result1.xlsx").is_file()
    assert (FINAL_ROOT / "result2.xlsx").is_file()
    assert (FINAL_ROOT / "Q1_MANIFEST.json").is_file()
    assert not list(FINAL_ROOT.glob("*.xls"))


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
    assert assert_deliverable_output(FINAL_ROOT / "result2.xlsx") == FINAL_ROOT / "result2.xlsx"


def test_formal_evidence_records_are_scoped_and_traceable() -> None:
    experiments = (ROOT / "docs" / "EXPERIMENTS.md").read_text(encoding="utf-8")
    assert re.search(r"EXP-001", experiments)
    assert re.search(r"EXP-007", experiments)
    for evidence_dir in sorted((ROOT / "experiments").glob("EXP-*/")):
        assert evidence_dir.parent == ROOT / "experiments"
        assert (evidence_dir / "config.json").is_file()
        assert (evidence_dir / "metrics.json").is_file()
        assert (evidence_dir / "notes.md").is_file()
    assert all(path.name in {"result1.xlsx", "result2.xlsx", "result3.xlsx", "result4.xlsx"} for path in CANDIDATE_ROOT.glob("*.xlsx") if not path.name.startswith("~$"))
    assert {path.name for path in FINAL_ROOT.glob("*.xlsx")} == {"result1.xlsx", "result2.xlsx"}


def test_state_preserves_question_boundaries() -> None:
    state = (ROOT / "docs" / "STATE.md").read_text(encoding="utf-8")
    assert "Q1" in state
    assert "Q2" in state
    assert "Q2 | FROZEN" in state or "| Q2 | FROZEN" in state
    assert "Q3 | CANDIDATE COMPLETE" in state or "| Q3 | CANDIDATE COMPLETE" in state
    assert "Q4 | CANDIDATE COMPLETE" in state or "| Q4 | CANDIDATE COMPLETE" in state
