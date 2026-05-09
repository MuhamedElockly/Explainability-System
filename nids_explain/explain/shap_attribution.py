"""Kernel SHAP attribution for predicted-class softmax mass."""

from typing import Optional

import numpy as np
import shap

from nids_explain.config import RNG_SEED, SHAP_BG_MAX, SHAP_NSAMPLES, TOP_SHAP_FEATURES


def build_shap_background(background_windows: np.ndarray, exclude_index: int, max_samples: int) -> np.ndarray:
    """
    Background for Kernel SHAP: other stratified windows only (exclude the explained instance)
    to reduce self-reference bias and improve attribution stability.
    """
    indices = [j for j in range(len(background_windows)) if j != exclude_index]
    if not indices:
        flat = background_windows.reshape(background_windows.shape[0], -1)
        return flat[:1]
    take = min(len(indices), max_samples)
    rng = np.random.default_rng(RNG_SEED + exclude_index)
    chosen = rng.choice(indices, size=take, replace=len(indices) < take)
    return background_windows[chosen].reshape(take, -1)


def compute_shap_top_features(
    model,
    sample_window,
    feature_names,
    pred_idx,
    background_windows,
    sample_index: int,
    top_k: Optional[int] = None,
):
    """
    Kernel SHAP on the predicted class softmax probability.
    Aggregates |SHAP| over time steps per feature (standard for sequence windows).
    """
    if top_k is None:
        top_k = TOP_SHAP_FEATURES
    time_steps, feat_count = sample_window.shape
    sample_flat = sample_window.reshape(1, -1)
    background_flat = build_shap_background(background_windows, sample_index, SHAP_BG_MAX)

    def class_predict(flat_x):
        batch = flat_x.reshape(-1, time_steps, feat_count).astype("float32")
        return model.predict(batch, verbose=0)[:, pred_idx]

    explainer = shap.KernelExplainer(class_predict, background_flat)
    shap_values = explainer.shap_values(sample_flat, nsamples=SHAP_NSAMPLES)
    shap_array = np.asarray(shap_values).reshape(time_steps, feat_count)

    mean_abs = np.mean(np.abs(shap_array), axis=0)
    mean_signed = np.mean(shap_array, axis=0)
    top_idx = np.argsort(mean_abs)[-top_k:][::-1]

    return [
        {
            "feature": str(feature_names[i]),
            "mean_abs_shap": float(mean_abs[i]),
            "mean_signed_shap": float(mean_signed[i]),
        }
        for i in top_idx
    ], {
        "shap_nsamples": SHAP_NSAMPLES,
        "background_size": int(background_flat.shape[0]),
        "exclude_index": sample_index,
        "target": "softmax_probability_for_predicted_class",
    }
