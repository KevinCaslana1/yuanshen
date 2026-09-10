import json
from pathlib import Path

from scripts.validate_deliverable_contract import validate_contract


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
    assert config["contract_status"] == "OPEN_QUESTION"
    for item in config["deliverables"]:
        for sheet in item["sheets"]:
            assert sheet["validation_status"] == "OPEN_QUESTION"
            assert sheet["expected_final_shape"]["status"] == "OPEN_QUESTION"
