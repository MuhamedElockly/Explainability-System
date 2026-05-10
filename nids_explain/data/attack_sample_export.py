"""Build a stratified attack-only CSV sample from the main flow dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from nids_explain.config import ATTACK_SAMPLE_MAX_ROWS, ATTACK_SAMPLE_SCAN_NROWS, ATTACK_SAMPLE_SEED
from nids_explain.data.labels import group_labels_to_8_classes

_LABEL_PRIORITY = ("label", "Label", "attack", "Attack", "class", "target")


def detect_label_column(df: pd.DataFrame, trained_features: list) -> str:
    feat = set(trained_features)
    for name in _LABEL_PRIORITY:
        if name in df.columns and name not in feat:
            return name
    extra = [c for c in df.columns if c not in feat]
    if not extra:
        raise ValueError("Could not infer label column — no CSV column outside trained features.")
    return extra[-1]


def export_attack_sample_csv(
    *,
    source_csv: str | Path,
    output_csv: str | Path,
    trained_features: list,
    scan_nrows: Optional[int] = None,
    max_rows: int | None = None,
    seed: int | None = None,
    per_class_floor: int | None = None,
) -> Path:
    """
    Read up to scan_nrows from source CSV, keep rows whose raw label maps to a non-BENIGN coarse class,
    then stratified sample up to max_rows across coarse attack families.

    Writes the same columns as present in the filtered frame (typically all features + label).
    """
    scan_nrows = ATTACK_SAMPLE_SCAN_NROWS if scan_nrows is None else int(scan_nrows)
    max_rows = ATTACK_SAMPLE_MAX_ROWS if max_rows is None else int(max_rows)
    seed = ATTACK_SAMPLE_SEED if seed is None else int(seed)
    floor = (
        max(10, max_rows // 12)
        if per_class_floor is None
        else int(per_class_floor)
    )

    src = Path(source_csv)
    out = Path(output_csv)
    if not src.exists():
        raise FileNotFoundError(f"Source CSV missing: {src}")

    df = pd.read_csv(src, nrows=scan_nrows)
    label_col = detect_label_column(df, trained_features)
    df["_coarse"] = (
        df[label_col].astype(str).str.strip().map(lambda x: group_labels_to_8_classes(x))
    )
    attack_df = df[df["_coarse"] != "BENIGN"]
    if attack_df.empty:
        raise RuntimeError(
            f"No attack rows found in first {scan_nrows} rows of {src}. Increase ATTACK_SAMPLE_SCAN_NROWS."
        )

    coarse_groups = list(attack_df.groupby("_coarse", sort=True))
    n_cls = len(coarse_groups)
    per_budget = max(floor, max_rows // max(n_cls, 1))

    rng = np.random.default_rng(seed)
    sampled_parts = []
    for coarse, grp in coarse_groups:
        take = min(len(grp), per_budget)
        if take <= 0:
            continue
        idx = rng.choice(len(grp), size=take, replace=False)
        sampled_parts.append(grp.iloc[np.sort(idx)])

    out_df = pd.concat(sampled_parts, axis=0)
    out_df = out_df.drop(columns=["_coarse"])
    if len(out_df) > max_rows:
        drop_idx = rng.choice(len(out_df), size=max_rows, replace=False)
        out_df = out_df.iloc[np.sort(drop_idx)]

    out.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out, index=False)
    return out
