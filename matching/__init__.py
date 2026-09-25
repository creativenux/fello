"""
matching

Rules-based peer group matching engine: hard-rule eligibility filtering,
weighted Gower similarity, group assembly (greedy construction plus
local-swap refinement), baselines, and a plain-language explainability
layer. Consumes the dataset produced by dataset_generation/ without
modifying it.

Author: Toheeb Olayemi (2516683), University of Chester.
"""

import paths  # noqa: F401  (puts dataset_generation/ on the import path)
