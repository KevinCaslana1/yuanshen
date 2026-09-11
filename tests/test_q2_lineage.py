import json
from pathlib import Path

import pytest

from src.q2.lineage import canonical_csv_path, canonical_path, load_canonical_manifest, production_csv_path


ROOT = Path(__file__).resolve().parents[1]


def test_project_q2_manifest_accepts_production_and_rejects_validation_artifacts() -> None:
    manifest = load_canonical_manifest(ROOT / "experiments" / "Q2_CANONICAL_DATA_MANIFEST.json")
    production = production_csv_path("experiments/Q2_FREEZE_RUN/run_1/official_samples.csv", verify_hash=False)
    assert production.is_file()
    with pytest.raises(ValueError, match="refusing noncanonical"):
        canonical_csv_path("experiments/EXP-Q2-016-LONG-ENV-A-last-raw/official_samples_recovered.csv", verify_hash=False)
    with pytest.raises(ValueError, match="refusing noncanonical"):
        canonical_path("experiments/EXP-Q2-016-LONG-ENV-A-last-raw/official_samples.csv", verify_hash=False)
    assert manifest["consumer_policy"]["reject_noncanonical"] is True


def test_lineage_guard_verifies_hashes_for_small_manifest(tmp_path: Path) -> None:
    data = tmp_path / "canonical.csv"
    data.write_text("time_s,value\n0,1\n", encoding="utf-8")
    import hashlib

    digest = hashlib.sha256(data.read_bytes()).hexdigest()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_version": "Q2_CANONICAL_DATA_MANIFEST_V1",
                "entries": [{"path": "canonical.csv", "sha256": digest, "status": "RECOVERED_CANONICAL"}],
            }
        ),
        encoding="utf-8",
    )
    assert canonical_path("canonical.csv", manifest_path=manifest, root_dir=tmp_path).read_text(encoding="utf-8").startswith("time_s")
    data.write_text("time_s,value\n0,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="hash mismatch"):
        canonical_path("canonical.csv", manifest_path=manifest, root_dir=tmp_path)
