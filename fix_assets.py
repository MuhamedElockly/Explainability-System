"""Validate model artifacts, clear app caches, optionally remove generated PDF reports."""

import json
import os
import shutil
import zipfile
from pathlib import Path

from nids_explain.config import (
    ARTIFACTS_DIR,
    ENCODER_FILENAME,
    FEATURES_FILENAME,
    INCIDENT_REPORTS_DIR,
    LEGACY_REPORT_FILE,
    MODEL_FILENAME,
    SCALAR_FILENAME,
)

REQUIRED_ARTIFACTS = [
    MODEL_FILENAME,
    ENCODER_FILENAME,
    SCALAR_FILENAME,
    FEATURES_FILENAME,
]


def clear_pycache(root: Path) -> int:
    deleted = 0
    for cache_dir in root.rglob("__pycache__"):
        shutil.rmtree(cache_dir, ignore_errors=True)
        deleted += 1
    return deleted


def clear_pyc_files(root: Path) -> int:
    n = 0
    for p in root.rglob("*.pyc"):
        try:
            p.unlink()
            n += 1
        except OSError:
            pass
    return n


def clear_optional_caches(root: Path) -> None:
    for name in (".pytest_cache", ".mypy_cache"):
        p = root / name
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
            print(f"Removed: {p}")


def clean_generated_reports(root: Path) -> None:
    """Remove legacy consolidated PDF (if present), incident PDFs, and caches."""
    pdf_main = Path(LEGACY_REPORT_FILE)
    if pdf_main.exists():
        pdf_main.unlink()
        print(f"Removed: {pdf_main}")

    inc_dir = INCIDENT_REPORTS_DIR
    if inc_dir.is_dir():
        for f in inc_dir.glob("*.pdf"):
            f.unlink()
            print(f"Removed: {f}")


def validate_model_archive(model_path: Path) -> None:
    if not model_path.exists():
        raise FileNotFoundError(f"Missing model file: {model_path}")
    with zipfile.ZipFile(model_path, "r") as zf:
        names = set(zf.namelist())
        if "config.json" not in names:
            raise RuntimeError("Model archive is missing config.json")
        json.loads(zf.read("config.json"))


def main():
    root = Path.cwd()
    print(f"Working directory: {root}")
    print(f"Artifact directory: {ARTIFACTS_DIR}")

    n_cache = clear_pycache(root)
    print(f"Removed __pycache__ folders: {n_cache}")
    n_pyc = clear_pyc_files(root)
    print(f"Removed stray .pyc files: {n_pyc}")
    clear_optional_caches(root)

    # CLEAN_REPORTS=1 — delete ids_inference_report.pdf and incident_reports/*.pdf
    if os.environ.get("CLEAN_REPORTS", "").strip() in ("1", "true", "True", "yes"):
        clean_generated_reports(root)
        print("CLEAN_REPORTS: generated PDFs cleared.")

    missing = [name for name in REQUIRED_ARTIFACTS if not (ARTIFACTS_DIR / name).exists()]
    if missing:
        print("Missing required files under model_artifacts/:")
        for item in missing:
            print(f" - {item}")
        raise SystemExit(1)

    validate_model_archive(ARTIFACTS_DIR / MODEL_FILENAME)
    print("Assets check passed.")


if __name__ == "__main__":
    main()
