"""Random sliding windows from raw CSV — features only (labels are never passed to the model)."""

from typing import Optional, Tuple

import numpy as np
import pandas as pd

from nids_explain.config import RNG_SEED, WINDOW_ROWS


def _numeric_feature_frame(df: pd.DataFrame, trained_features: list) -> pd.DataFrame:
    out = df[trained_features].apply(pd.to_numeric, errors="coerce").fillna(0)
    out.replace([np.inf, -np.inf], 0, inplace=True)
    return out


def sample_random_windows(
    df_raw: pd.DataFrame,
    trained_features: list,
    scaler,
    n_windows: int,
    window_rows: int = WINDOW_ROWS,
    seed: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Draw random contiguous windows of `window_rows` rows each.
    Returns (windows float32 array [n, window_rows, F], start_indices int64 [n]).
    """
    if seed is None:
        seed = RNG_SEED
    data = _numeric_feature_frame(df_raw, trained_features)
    n = len(data)
    if n < window_rows:
        raise ValueError(f"Need at least {window_rows} rows; got {n}")

    max_start = n - window_rows
    rng = np.random.default_rng(seed)
    # Unique random start positions when possible
    count = min(n_windows, max_start + 1)
    if count <= 0:
        raise ValueError("No valid windows")
    replace = count > (max_start + 1)
    starts = rng.choice(max_start + 1, size=count, replace=replace)

    windows = []
    for s in starts:
        chunk = data.iloc[int(s) : int(s) + window_rows]
        windows.append(scaler.transform(chunk.values))
    return np.asarray(windows, dtype=np.float32), starts.astype(np.int64)


def sample_background_windows(
    df_raw: pd.DataFrame,
    trained_features: list,
    scaler,
    n_windows: int,
    window_rows: int = WINDOW_ROWS,
    seed_offset: int = 0,
) -> np.ndarray:
    """Extra random windows for Kernel SHAP background (features only)."""
    return sample_random_windows(
        df_raw,
        trained_features,
        scaler,
        n_windows,
        window_rows=window_rows,
        seed=RNG_SEED + 1337 + seed_offset,
    )[0]
