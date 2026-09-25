"""
attributes.py

The matching attributes, their types, their matching logic (homogeneity or
complementarity), their category orders, and their weights. 
This is configuration only.

Weights: the eight weights from the master design specification (Section 5),
renormalised proportionally after communication modality (0.08) was removed
from the dataset, i.e. each original weight divided by 0.92. They are a defensible starting
configuration, not a finding, and are tested by the sensitivity analysis.

Category orders are read from schema.py so they can never drift from the
generator.

Author: Toheeb Olayemi (2516683), University of Chester.
"""

from __future__ import annotations

from schema import CONFIG, ALL_SUBTYPES, DURATION_BANDS

NOMINAL, ORDINAL, NUMERIC = "nominal", "ordinal", "numeric"
HOMOGENEITY, COMPLEMENTARITY = "homogeneity", "complementarity"

# Isolation score bands used for the complementarity entropy term, from the
# trial categorisation already documented in schema.py (20-34 low, 35-49
# moderate, 50-64 moderately high, 65-80 high; NCT03442296). Each entry is
# (label, lower bound inclusive).
ISOLATION_BANDS = [
    ("low", 20.0),
    ("moderate", 35.0),
    ("moderately high", 50.0),
    ("high", 65.0),
]

# column -> type, logic, ordered categories (None for numeric), plain label
ATTRIBUTES = {
    "primary_condition_subtype": {
        "type": NOMINAL, "logic": HOMOGENEITY,
        "categories": list(ALL_SUBTYPES), "label": "condition sub-type",
    },
    "primary_support_goal": {
        "type": NOMINAL, "logic": HOMOGENEITY,
        "categories": list(CONFIG["primary_support_goal"]), "label": "support goal",
    },
    "support_orientation": {
        "type": ORDINAL, "logic": COMPLEMENTARITY,
        "categories": ["Seeking", "Balanced", "Offering"], "label": "support orientation",
    },
    "age_band": {
        "type": ORDINAL, "logic": HOMOGENEITY,
        "categories": list(CONFIG["age_band_weights"]), "label": "age band",
    },
    "condition_duration_band": {
        "type": ORDINAL, "logic": HOMOGENEITY,
        "categories": list(DURATION_BANDS), "label": "time lived with the condition",
    },
    "psychosocial_isolation_score": {
        "type": NUMERIC, "logic": COMPLEMENTARITY,
        "categories": [label for label, _ in ISOLATION_BANDS], "label": "isolation level",
    },
    "gender": {
        "type": NOMINAL, "logic": HOMOGENEITY,
        "categories": list(CONFIG["gender"]), "label": "gender",
    },
    "engagement_level": {
        "type": ORDINAL, "logic": HOMOGENEITY,
        "categories": ["Low", "Medium", "High"], "label": "engagement level",
    },
}

DEFAULT_WEIGHTS = {
    "primary_condition_subtype": 0.2174,
    "primary_support_goal": 0.1957,
    "support_orientation": 0.1304,
    "age_band": 0.1304,
    "condition_duration_band": 0.1087,
    "psychosocial_isolation_score": 0.1087,
    "gender": 0.0543,
    "engagement_level": 0.0543,
}

HOMOGENEITY_ATTRIBUTES = [a for a, s in ATTRIBUTES.items() if s["logic"] == HOMOGENEITY]
COMPLEMENTARITY_ATTRIBUTES = [a for a, s in ATTRIBUTES.items() if s["logic"] == COMPLEMENTARITY]

# Hard-rule constants (group size per the six-to-eight
# justification document, docs/Justification for a Peer Group Size of Six to
# Eight Members.pdf).
MIN_GROUP_SIZE = 6
MAX_GROUP_SIZE = 8
TARGET_GROUP_SIZE = 7
POOL_KEYS = ("primary_condition_category", "communication_language")


def equal_weights() -> dict:
    """Every attribute weighted equally (the unweighted-Gower baseline)."""
    return {a: 1.0 / len(ATTRIBUTES) for a in ATTRIBUTES}


def homogeneity_weights(weights: dict) -> dict:
    """Restrict weights to homogeneity attributes and renormalise to sum to 1."""
    sub = {a: weights[a] for a in HOMOGENEITY_ATTRIBUTES}
    total = sum(sub.values())
    if total <= 0:
        raise ValueError("homogeneity weights sum to zero; cannot renormalise")
    return {a: w / total for a, w in sub.items()}


def isolation_band(score: float) -> str:
    """Map an isolation score to its trial band label."""
    label = ISOLATION_BANDS[0][0]
    for name, lower in ISOLATION_BANDS:
        if score >= lower:
            label = name
    return label
