"""
Export a stratified attack-only CSV into sample_datasets/attacks_sample.csv

Uses DATASET_CSV or resolve_dataset_path(), feature_names.joblib from model_artifacts, and the same
coarse labeling as nids_explain.data.labels.group_labels_to_8_classes.

Environment (optional overrides, see nids_explain/config.py):
  ATTACK_SAMPLE_MAX_ROWS, ATTACK_SAMPLE_SCAN_NROWS, ATTACK_SAMPLE_SEED
"""

from pathlib import Path

import joblib

from nids_explain.config import (
    ATTACK_SAMPLE_MAX_ROWS,
    DEFAULT_ATTACK_SAMPLE_CSV,
    FEATURES_FILE,
)
from nids_explain.core.env_loader import load_local_env
from nids_explain.data.attack_sample_export import export_attack_sample_csv
from nids_explain.data.dataset import resolve_dataset_path


def main():
    load_local_env()
    features = joblib.load(FEATURES_FILE)
    if not isinstance(features, list):
        raise SystemExit(f"Unexpected FEATURES_FILE format: {type(features)}")
    csv_path = resolve_dataset_path()
    out = DEFAULT_ATTACK_SAMPLE_CSV

    wrote = export_attack_sample_csv(
        source_csv=csv_path,
        output_csv=out,
        trained_features=features,
    )

    sz_mb = wrote.stat().st_size / (1024 * 1024)
    print(f"Wrote {wrote.relative_to(Path(__file__).resolve().parent)}")
    print(f"  source: {csv_path}")
    print(f"  rows cap: ~{ATTACK_SAMPLE_MAX_ROWS} (stratified), scan up to ATTACK_SAMPLE_SCAN_NROWS lines")
    print(f"  size: {sz_mb:.2f} MiB")


if __name__ == "__main__":
    main()
