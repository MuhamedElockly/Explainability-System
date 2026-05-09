"""Formatting and ranking helpers for softmax outputs."""

import numpy as np


def fmt_prob(value) -> str:
    if value is None:
        return "n/a"
    try:
        x = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if x != x:  # NaN
        return "n/a"
    return f"{x:.6f}"


def top_k_class_string(probs: np.ndarray, class_names: list, k: int = 3) -> str:
    probs = np.asarray(probs).ravel()
    k = min(k, len(probs))
    idx = np.argsort(probs)[-k:][::-1]
    return "; ".join(f"{class_names[j]}: {float(probs[j]):.4f}" for j in idx)
