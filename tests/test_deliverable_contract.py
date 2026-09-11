import json
from pathlib import Path

from scripts.validate_deliverable_contract import validate_contract
from scripts.validate_q1_candidate import validate_candidate


ROOT = Path(__file__).resolve().parents[1]


def test_deliverable_contract_is_valid() -> None:
    assert validate_contract(ROOT) == []


def test_contract_registers_four_questions_and_no_predictions() -> None:
    config = json.loads((ROOT / "config" / "deliverables.json").read_text(encoding="utf-8"))
    assert {item["question"] for item in config["deliverables"]} == {"Q1", "Q2", "Q3", "Q4"}
    serialized = json.dumps(config, ensure_ascii=False)
    assert "prediction" not in serialized.lower()
    assert "answer" not in serialized.lower()


def test_open_questions_are_not_verified() -> None:
    config = json.loads((ROOT / "config" / "deliverables.json").read_text(encoding="utf-8"))
    assert config["contract_status"] == "Q1_CONTRACT_FROZEN_Q2_Q4_OPEN"
    for item in config["deliverables"]:
        for sheet in item["sheets"]:
            if item["question"] == "Q1":
                assert sheet["validation_status"] == "Q1_CONTRACT_FROZEN_PENDING_ACCURACY"
                assert sheet["expected_final_shape"] == {
                    "status": "FROZEN_Q1_CONTRACT",
                    "rows": 1801,
                    "columns": 22,
                    "known_rule": "表头1行 + 1800个时间数据行；A列时间 + 21个空间列",
                }
                assert sheet["open_questions"] == []
            else:
                assert sheet["validation_status"] == "OPEN_QUESTION"
                assert sheet["expected_final_shape"]["status"] == "OPEN_QUESTION"


def test_q1_candidate_validator_fails_closed_when_candidate_is_absent() -> None:
    errors = validate_candidate(ROOT)
    assert any("missing Q1 candidate workbook" in error for error in errors)
