from pathlib import Path

from scripts.validate_templates import TEMPLATES, check_template


ROOT = Path(__file__).resolve().parents[1]


def test_official_template_contracts() -> None:
    for relative, spec in TEMPLATES.items():
        assert check_template(ROOT, relative, spec) == []


def test_template_paths_are_not_candidate_or_final_paths() -> None:
    for relative in TEMPLATES:
        assert not relative.startswith("deliverables/candidate/")
        assert not relative.startswith("deliverables/final/")
