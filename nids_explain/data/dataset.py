"""Dataset path resolution."""

import os
from pathlib import Path

from nids_explain.config import DEFAULT_DATASET_REL


def resolve_dataset_path():
    env_path = os.getenv("DATASET_CSV")
    candidates = [env_path, DEFAULT_DATASET_REL]
    candidates.extend(
        [
            "/mnt/f/courses/Master/Offinsive And Deffensife Cyper Security/Datasets & Models/unp-cic-iot-2023/wataiData/csv/CICIoT2023/part-00000-363d1ba3-8ab5-4f96-bc25-4d5862db7cb9-c000.csv",
            str(Path.cwd() / DEFAULT_DATASET_REL),
        ]
    )
    for path in candidates:
        if path and Path(path).exists():
            return path
    raise FileNotFoundError(
        "Dataset CSV not found. Set DATASET_CSV env var or place the file at "
        f"'{DEFAULT_DATASET_REL}'."
    )
