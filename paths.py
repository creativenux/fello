"""
paths.py

One place that says where things live, so every script reads and writes the
same folders no matter which directory it is run from.

  fello/dataset_generation/   the synthetic data generator (unchanged code)
  fello/output/n<n>/          generated datasets, validation reports, figures
  fello/output/matching/      matching results

"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GENERATOR_DIR = ROOT / "dataset_generation"
OUTPUT_DIR = ROOT / "output"
MATCHING_DIR = OUTPUT_DIR / "matching"

if str(GENERATOR_DIR) not in sys.path:
    sys.path.insert(0, str(GENERATOR_DIR))


def dataset_dir(n: int) -> Path:
    """Folder for datasets of size n (kept apart so sizes never overwrite each other)."""
    return OUTPUT_DIR / f"n{n}"


def dataset_csv(n: int, seed: int) -> Path:
    return dataset_dir(n) / f"profiles_seed{seed}.csv"
