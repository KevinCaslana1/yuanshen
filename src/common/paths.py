"""Path guards for official sources and deliverable outputs."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OFFICIAL_ROOT = (PROJECT_ROOT / "A题").resolve()
CANDIDATE_ROOT = (PROJECT_ROOT / "deliverables" / "candidate").resolve()
FINAL_ROOT = (PROJECT_ROOT / "deliverables" / "final").resolve()


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    return candidate.resolve()


def assert_not_official_output(path: str | Path) -> Path:
    """Reject any future output path inside the immutable official source."""

    resolved = resolve_project_path(path)
    if _is_within(resolved, OFFICIAL_ROOT):
        raise ValueError(f"Refusing to write inside OFFICIAL_SOURCE: {resolved}")
    return resolved


def assert_deliverable_output(path: str | Path) -> Path:
    """Require a future output path to be under candidate or final."""

    resolved = assert_not_official_output(path)
    if not (_is_within(resolved, CANDIDATE_ROOT) or _is_within(resolved, FINAL_ROOT)):
        raise ValueError(f"Output must be under candidate or final deliverables: {resolved}")
    return resolved
