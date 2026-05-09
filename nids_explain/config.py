"""Paths, hyperparameters, and reproducibility seed for the IDS explainability pipeline."""

import os
from pathlib import Path

import numpy as np

# Project root = parent of the `nids_explain` package (your "Explainability System" folder).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Trained model + sklearn artifacts live here (not in the package source tree).
ARTIFACTS_DIR = _PROJECT_ROOT / "model_artifacts"

MODEL_FILENAME = "iot_model_20260507_171659.keras"
ENCODER_FILENAME = "label_encoder.joblib"
SCALAR_FILENAME = "scaler.joblib"
FEATURES_FILENAME = "feature_names.joblib"

MODEL_FILE = str(ARTIFACTS_DIR / MODEL_FILENAME)
ENCODER_FILE = str(ARTIFACTS_DIR / ENCODER_FILENAME)
SCALAR_FILE = str(ARTIFACTS_DIR / SCALAR_FILENAME)
FEATURES_FILE = str(ARTIFACTS_DIR / FEATURES_FILENAME)

DEFAULT_DATASET_REL = "CICIoT2023/part-00000-363d1ba3-8ab5-4f96-bc25-4d5862db7cb9-c000.csv"

RNG_SEED = int(os.environ.get("EXPLAIN_SEED", "42"))
np.random.seed(RNG_SEED)

TOP_SHAP_FEATURES = int(os.environ.get("TOP_SHAP_FEATURES", "10"))
SHAP_NSAMPLES = int(os.environ.get("SHAP_NSAMPLES", "256"))
SHAP_BG_MAX = int(os.environ.get("SHAP_BG_MAX", "16"))

# Blind inference: random windows from CSV using feature columns only (label never fed to the model).
WINDOW_ROWS = int(os.environ.get("WINDOW_ROWS", "10"))
# Random blind windows per run; consolidated stratified report removed — this is the main knob.
BLIND_SAMPLE_COUNT = int(os.environ.get("BLIND_SAMPLE_COUNT", "8"))
BLIND_BACKGROUND_WINDOWS = int(os.environ.get("BLIND_BACKGROUND_WINDOWS", "24"))
CSV_READ_NROWS = int(os.environ.get("CSV_READ_NROWS", "800000"))

# Per-incident PDFs (attack predictions only)
INCIDENT_REPORTS_DIR = _PROJECT_ROOT / os.environ.get("INCIDENT_REPORTS_DIR", "incident_reports")

# Legacy consolidated PDF filename (fix_assets CLEAN_REPORTS only)
_LEGACY_REPORT = os.environ.get("REPORT_FILENAME", "ids_inference_report.pdf")
LEGACY_REPORT_FILE = str(_PROJECT_ROOT / _LEGACY_REPORT)
