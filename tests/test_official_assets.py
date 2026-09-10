from pathlib import Path

from scripts.validate_inputs import EXPECTED, sha256


ROOT = Path(__file__).resolve().parents[1]


def test_official_asset_manifest_matches_files() -> None:
    for relative, expected in EXPECTED.items():
        path = ROOT / relative
        assert path.is_file(), relative
        assert path.stat().st_size == expected["bytes"], relative
        assert sha256(path) == expected["sha256"], relative


def test_official_assets_stay_under_official_root() -> None:
    official_root = (ROOT / "A题").resolve()
    for relative in EXPECTED:
        path = (ROOT / relative).resolve()
        assert official_root in path.parents, relative
