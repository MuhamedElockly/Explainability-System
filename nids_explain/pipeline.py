"""End-to-end IDS inference: blind feature windows → SHAP → Gemini → one PDF per attack incident."""

import time

import joblib
import numpy as np
import pandas as pd

import nids_explain.core.tf_setup  # noqa: F401 — side effects before model load

from nids_explain.config import (
    BLIND_BACKGROUND_WINDOWS,
    BLIND_SAMPLE_COUNT,
    CSV_READ_NROWS,
    ENCODER_FILE,
    FEATURES_FILE,
    GEMINI_INTER_REQUEST_DELAY_SEC,
    INCIDENT_REPORTS_DIR,
    MODEL_FILE,
    SCALAR_FILE,
    SHAP_NSAMPLES,
    TOP_SHAP_FEATURES,
    RNG_SEED,
)
from nids_explain.core.env_loader import load_local_env
from nids_explain.data.blind_sampling import sample_background_windows, sample_random_windows
from nids_explain.data.dataset import resolve_dataset_path
from nids_explain.explain.shap_attribution import compute_shap_top_features
from nids_explain.llm.attack_kb import get_attack_context
from nids_explain.llm.gemini import generate_blind_incident_report, init_gemini
from nids_explain.model.loader import load_and_patch_model
from nids_explain.report.incident_pdf import incident_pdf_path, write_incident_pdf
from nids_explain.utils.probability import top_k_class_string


def _load_artifacts_and_model():
    le = joblib.load(ENCODER_FILE)
    trained_features = joblib.load(FEATURES_FILE)
    scaler = joblib.load(SCALAR_FILE)
    model = load_and_patch_model(MODEL_FILE)
    return le, trained_features, scaler, model


def run_blind_incidents(le, trained_features, scaler, model, gemini_bundle, dataset_csv: str) -> None:
    """
    Random windows from CSV using feature columns only (label column never fed to the model).
    For each attack prediction: SHAP + vector RAG retrieval + Gemini + separate incident PDF.
    """
    df_raw = pd.read_csv(dataset_csv, nrows=CSV_READ_NROWS)
    blind_windows, row_starts = sample_random_windows(
        df_raw,
        trained_features,
        scaler,
        BLIND_SAMPLE_COUNT,
    )
    extra_bg = sample_background_windows(
        df_raw,
        trained_features,
        scaler,
        BLIND_BACKGROUND_WINDOWS,
    )
    shap_pool = np.concatenate([blind_windows, extra_bg], axis=0)

    print(
        f"Samples: {len(blind_windows)} windows (features only). "
        f"EXPLAIN_SEED={RNG_SEED}. SHAP background pool: {shap_pool.shape[0]} windows."
    )
    preds = model.predict(blind_windows, batch_size=32, verbose=0)
    class_names = [str(c) for c in le.classes_]

    INCIDENT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    incident_seq = 0
    llm_calls = 0

    for i in range(len(blind_windows)):
        probs = np.asarray(preds[i]).ravel()
        pred_idx = int(np.argmax(probs))
        pred_name = str(class_names[pred_idx])
        confidence = float(np.max(probs) * 100.0)
        top3_str = top_k_class_string(probs, class_names, k=3)

        if pred_name == "BENIGN":
            print(f"  [{i}] row≈{row_starts[i]} → BENIGN ({confidence:.2f}%) — skip PDF")
            continue

        print(f"  [{i}] row≈{row_starts[i]} → {pred_name} ({confidence:.2f}%) — SHAP + PDF")
        shap_top_features, shap_meta = compute_shap_top_features(
            model=model,
            sample_window=blind_windows[i],
            feature_names=trained_features,
            pred_idx=pred_idx,
            background_windows=shap_pool,
            sample_index=i,
            top_k=TOP_SHAP_FEATURES,
        )
        event = {
            "predicted_class": pred_name,
            "confidence": confidence,
            "top3_str": top3_str,
            "shap_top_features": shap_top_features,
            "shap_meta": shap_meta,
            "row_start": int(row_starts[i]),
        }
        rag_context = get_attack_context(pred_name, event)
        if llm_calls > 0 and GEMINI_INTER_REQUEST_DELAY_SEC > 0:
            time.sleep(GEMINI_INTER_REQUEST_DELAY_SEC)
        llm_text = generate_blind_incident_report(gemini_bundle, event, rag_context)
        llm_calls += 1

        out_pdf = incident_pdf_path(INCIDENT_REPORTS_DIR, incident_seq, pred_name)
        meta_pdf = {
            "row_start": int(row_starts[i]),
            "shap_nsamples": shap_meta.get("shap_nsamples", SHAP_NSAMPLES),
            "background_pool": shap_pool.shape[0],
        }
        write_incident_pdf(
            out_pdf,
            predicted_class=pred_name,
            confidence_pct=confidence,
            top3_str=top3_str,
            shap_features=shap_top_features,
            llm_narrative=llm_text,
            rag_context=rag_context,
            meta=meta_pdf,
        )
        incident_seq += 1
        print(f"      → {out_pdf}")

    if incident_seq == 0:
        print("No attack-class predictions in this batch — no incident PDFs.")
    else:
        print(f"\nDone: {incident_seq} incident PDF(s) in {INCIDENT_REPORTS_DIR}")


def main():
    load_local_env()
    print("Initializing IDS explainability (incident PDFs only)...")
    le, trained_features, scaler, model = _load_artifacts_and_model()
    gemini_bundle, gemini_init_msg = init_gemini()
    if gemini_init_msg:
        print(gemini_init_msg)

    dataset_csv = resolve_dataset_path()
    print(f"Dataset: {dataset_csv}")

    if BLIND_SAMPLE_COUNT <= 0:
        raise SystemExit(
            "Set BLIND_SAMPLE_COUNT to a positive integer (e.g. BLIND_SAMPLE_COUNT=8). "
            "Stratified summary reports were removed."
        )

    run_blind_incidents(le, trained_features, scaler, model, gemini_bundle, dataset_csv)
