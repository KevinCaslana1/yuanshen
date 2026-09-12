"""Canonical-data lineage and fail-closed access guard for Q2 artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "experiments" / "Q2_CANONICAL_DATA_MANIFEST.json"
CANONICAL_STATUSES = frozenset({"CANONICAL", "RECOVERED_CANONICAL"})
PRODUCTION_CANONICAL_STATUS = "PRODUCTION_CANONICAL"
KNOWN_STATUSES = frozenset(
    {
        "CANONICAL",
        "RECOVERED_CANONICAL",
        "PRODUCTION_CANONICAL",
        "DETERMINISM_REFERENCE",
        "VALIDATION_ONLY",
        "NONCANONICAL_INTERRUPTED",
        "NONCANONICAL_DUPLICATE",
        "FAILED_PRODUCTION_ATTEMPT",
        "VALIDATION_EVIDENCE_ONLY",
        "NOT_DELIVERY_SOURCE",
        "NOT_CANONICAL_FOR_DELIVERY",
    }
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_canonical_manifest(manifest_path: str | Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    """Load and structurally validate the Q2 lineage manifest."""
    path = Path(manifest_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"canonical Q2 manifest not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("manifest_version") != "Q2_CANONICAL_DATA_MANIFEST_V1":
        raise ValueError("unsupported Q2 canonical manifest version")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("canonical manifest must contain non-empty entries")
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ValueError("canonical manifest entry is malformed")
        relative = Path(entry["path"]).as_posix()
        if relative in seen:
            raise ValueError(f"duplicate canonical manifest path: {relative}")
        seen.add(relative)
        if entry.get("status") not in KNOWN_STATUSES:
            raise ValueError(f"unknown canonical manifest status for {relative}")
        expected = entry.get("sha256", "")
        if not isinstance(expected, str) or len(expected) != 64:
            raise ValueError(f"invalid SHA-256 for {relative}")
    return payload


def canonical_path(
    relative_path: str | Path,
    *,
    manifest_path: str | Path = DEFAULT_MANIFEST,
    root_dir: str | Path = ROOT,
    verify_hash: bool = True,
) -> Path:
    """Resolve a file only when the manifest marks it canonical.

    Noncanonical interrupted/duplicate artifacts fail before opening the file.
    Hash verification remains enabled by default so a changed canonical file
    cannot silently enter figures, paper tables, or a future workbook.
    """
    payload = load_canonical_manifest(manifest_path)
    relative = Path(relative_path).as_posix()
    entries = {entry["path"]: entry for entry in payload["entries"]}
    entry = entries.get(relative)
    if entry is None:
        raise ValueError(f"path is not registered in the Q2 canonical manifest: {relative}")
    if entry["status"] not in CANONICAL_STATUSES:
        raise ValueError(f"refusing noncanonical Q2 artifact ({entry['status']}): {relative}")
    root = Path(root_dir).resolve()
    path = (root / relative).resolve()
    if root != path and root not in path.parents:
        raise ValueError(f"canonical path escapes project root: {relative}")
    if not path.is_file():
        raise FileNotFoundError(f"canonical Q2 artifact is missing: {path}")
    if verify_hash and _sha256(path).lower() != entry["sha256"].lower():
        raise ValueError(f"canonical Q2 artifact hash mismatch: {relative}")
    return path


def canonical_csv_path(relative_path: str | Path, **kwargs: Any) -> Path:
    """Resolve a canonical CSV through the same fail-closed guard."""
    path = canonical_path(relative_path, **kwargs)
    if path.suffix.lower() != ".csv":
        raise ValueError(f"canonical data loader requires a CSV path: {path}")
    return path


def production_canonical_path(
    relative_path: str | Path,
    *,
    manifest_path: str | Path = DEFAULT_MANIFEST,
    root_dir: str | Path = ROOT,
    verify_hash: bool = True,
) -> Path:
    """Resolve the sole approved Q2 production source, fail-closed.

    The older ``canonical_path`` API remains available for validation-era
    evidence.  Result workbooks and formal Q2 figures must use this stricter
    loader so recovered, duplicate, sensitivity, and determinism-reference
    artifacts cannot become the formal result source by accident.
    """
    payload = load_canonical_manifest(manifest_path)
    relative = Path(relative_path).as_posix()
    entries = {entry["path"]: entry for entry in payload["entries"]}
    entry = entries.get(relative)
    if entry is None:
        raise ValueError(f"path is not registered in the Q2 canonical manifest: {relative}")
    if entry["status"] != PRODUCTION_CANONICAL_STATUS:
        raise ValueError(f"refusing non-production Q2 artifact ({entry['status']}): {relative}")
    root = Path(root_dir).resolve()
    path = (root / relative).resolve()
    if root != path and root not in path.parents:
        raise ValueError(f"production canonical path escapes project root: {relative}")
    if not path.is_file():
        raise FileNotFoundError(f"production canonical Q2 artifact is missing: {path}")
    if verify_hash and _sha256(path).lower() != entry["sha256"].lower():
        raise ValueError(f"production canonical artifact hash mismatch: {relative}")
    return path


def production_csv_path(relative_path: str | Path, **kwargs: Any) -> Path:
    """Resolve a production-canonical CSV through the strict guard."""
    path = production_canonical_path(relative_path, **kwargs)
    if path.suffix.lower() != ".csv":
        raise ValueError(f"production data loader requires a CSV path: {path}")
    return path
