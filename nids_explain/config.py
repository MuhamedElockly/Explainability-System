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

# Stratified attack-only CSV sample (`export_attack_sample.py`). Not used automatically by pipeline.
ATTACK_SAMPLE_DIR = _PROJECT_ROOT / "sample_datasets"
DEFAULT_ATTACK_SAMPLE_CSV = ATTACK_SAMPLE_DIR / "attacks_sample.csv"
ATTACK_SAMPLE_MAX_ROWS = int(os.environ.get("ATTACK_SAMPLE_MAX_ROWS", "6000"))
ATTACK_SAMPLE_SCAN_NROWS = int(os.environ.get("ATTACK_SAMPLE_SCAN_NROWS", "500000"))
ATTACK_SAMPLE_SEED = int(os.environ.get("ATTACK_SAMPLE_SEED", str(RNG_SEED)))

# Per-incident PDFs (attack predictions only)
INCIDENT_REPORTS_DIR = _PROJECT_ROOT / os.environ.get("INCIDENT_REPORTS_DIR", "incident_reports")

# Legacy consolidated PDF filename (fix_assets CLEAN_REPORTS only)
_LEGACY_REPORT = os.environ.get("REPORT_FILENAME", "ids_inference_report.pdf")
LEGACY_REPORT_FILE = str(_PROJECT_ROOT / _LEGACY_REPORT)

# Gemini API (rate limits / quota — see https://ai.google.dev/gemini-api/docs/rate-limits)
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash").strip()
GEMINI_INTER_REQUEST_DELAY_SEC = float(os.environ.get("GEMINI_INTER_REQUEST_DELAY_SEC", "4"))
GEMINI_MAX_RETRIES = int(os.environ.get("GEMINI_MAX_RETRIES", "8"))
# GEMINI_DISABLE=1 → skip LLM calls; PDFs still use SHAP + retrieved RAG (or RAG_DISABLE static fallback).

# Vector RAG (Chroma + sentence-transformers). Persisted under project root.
RAG_PERSIST_DIR = _PROJECT_ROOT / os.environ.get("RAG_PERSIST_DIR", "rag_chroma").strip()
RAG_EMBEDDING_MODEL = os.environ.get("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2").strip()
RAG_TOP_K = int(os.environ.get("RAG_TOP_K", "6"))
RAG_TOP_K_FILTERED = int(os.environ.get("RAG_TOP_K_FILTERED", "4"))
RAG_QUERY_TOP_SHAP = int(os.environ.get("RAG_QUERY_TOP_SHAP", "8"))
RAG_PROMPT_MAX_CHARS = int(os.environ.get("RAG_PROMPT_MAX_CHARS", "12000"))
RAG_PDF_CONTEXT_MAX_CHARS = int(os.environ.get("RAG_PDF_CONTEXT_MAX_CHARS", "4500"))
