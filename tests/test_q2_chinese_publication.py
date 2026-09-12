"""Regression checks for the frozen-data-only Q2 Chinese figure package."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "experiments/Q2_CHINESE_FIGURE_LOCALIZATION/validation.json"
EXPECTED_SHA = "84fb32457193e158debdf569d34f5f41b97e78496b30dd9b2e134385439e10da"


def test_q2_chinese_package_is_pass_and_complete() -> None:
    record = json.loads(VALIDATION.read_text(encoding="utf-8"))
    package = record["q2_chinese_figure_localization"]
    assert record["status"] == "PASS"
    assert package["figure_count"] == 11
    assert package["png_count"] == 11
    assert package["svg_count"] == 11
    assert package["data_trace"] == "11/11"
    assert package["chinese_text_validation"] == "11/11"


def test_q2_chinese_pngs_have_at_least_300_dpi_and_svgs_have_chinese_text() -> None:
    record = json.loads(VALIDATION.read_text(encoding="utf-8"))
    for item in record["q2_chinese_figure_localization"]["items"]:
        png = ROOT / item["png"]
        svg = ROOT / item["svg"]
        with Image.open(png) as image:
            dpi = image.info["dpi"]
            assert float(dpi[0]) >= 300.0
            assert float(dpi[1]) >= 300.0
        svg_text = svg.read_text(encoding="utf-8")
        assert "□" not in svg_text
        assert any("\u3400" <= char <= "\u9fff" for char in svg_text)


def test_q2_result2_hash_is_unchanged_by_localization() -> None:
    record = json.loads(VALIDATION.read_text(encoding="utf-8"))
    freeze = record["q2_frozen_integrity"]
    assert freeze["sha256_before"] == EXPECTED_SHA
    assert freeze["sha256_after"] == EXPECTED_SHA
    assert freeze["sha256_current"] == EXPECTED_SHA
    assert freeze["numerical_result_changed"] is False
    assert freeze["frozen_original_q2_figures_unchanged"] is True


def test_q1_q3_q4_metadata_check_passes_without_redraw() -> None:
    record = json.loads(VALIDATION.read_text(encoding="utf-8"))
    metadata = record["q1_q3_q4_metadata_check"]
    assert metadata["status"] == "PASS"
    assert metadata["action"] == "no redraw required"
