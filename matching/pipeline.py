"""
pipeline.py

Runs the whole matching method and every baseline on one dataset:

    hard rules -> eligible pools -> for each viable pool, each method

and collects the results per method across all pools, with timings, so the
evaluation module, the API and the command line all use one code path.

Author: Toheeb Olayemi (2516683), University of Chester.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import pandas as pd

from matching.attributes import DEFAULT_WEIGHTS, MIN_GROUP_SIZE
from matching.baselines import random_assignment, single_attribute, unweighted_gower
from matching.explainability import explain_group
from matching.group_assembly import assemble_groups
from matching.hard_rules import HardRuleAudit, partition_into_eligible_pools
from matching.similarity import compute_gower_distance_matrix


def _weighted_gower(pool_df, seed, pool_key, weights=None):
    weights = weights or DEFAULT_WEIGHTS
    distance = compute_gower_distance_matrix(pool_df, weights)
    return assemble_groups(pool_df, distance, weights, seed=seed,
                           method="weighted_gower", pool_key=pool_key)


METHODS = {
    "weighted_gower": _weighted_gower,
    "unweighted_gower": lambda pool, seed, key: unweighted_gower(pool, seed=seed, pool_key=key),
    "single_age_band": lambda pool, seed, key: single_attribute(pool, "age_band", seed, key),
    "single_primary_support_goal":
        lambda pool, seed, key: single_attribute(pool, "primary_support_goal", seed, key),
    "random": lambda pool, seed, key: random_assignment(pool, seed=seed, pool_key=key),
}


@dataclass
class MethodOutcome:
    method: str
    pool_results: list = field(default_factory=list)   # GroupingResult per viable pool
    unmatched: dict = field(default_factory=dict)      # profile_id -> reason, all pools
    seconds: float = 0.0

    @property
    def groups(self) -> list:
        return [g for r in self.pool_results for g in r.groups]

    def group_records(self) -> list:
        """One record per group: id, pool, members, Score(G), details, explanation."""
        records = []
        for r in self.pool_results:
            for i, (members, score, detail) in enumerate(zip(r.groups, r.scores, r.group_details)):
                records.append({
                    "group_id": f"{self.method}|{r.pool_key[0]}|{r.pool_key[1]}|{i + 1}",
                    "category": r.pool_key[0], "language": r.pool_key[1],
                    "members": members, "score": score, "details": detail,
                    "explanation": explain_group(detail),
                })
        return records


@dataclass
class MatchingRun:
    seed: int
    n_profiles: int
    audit: HardRuleAudit
    pools: dict                                        # pool key -> pool DataFrame
    methods: dict = field(default_factory=dict)        # method name -> MethodOutcome


def run_all_methods(df: pd.DataFrame, seed: int = 0, methods: list | None = None) -> MatchingRun:
    """Apply the hard rules, then every requested method to every viable pool."""
    pools, audit = partition_into_eligible_pools(df)
    run = MatchingRun(seed=seed, n_profiles=len(df), audit=audit, pools=pools)
    for name in methods or list(METHODS):
        outcome = MethodOutcome(method=name, unmatched=dict(audit.excluded))
        start = time.perf_counter()
        for key, pool in pools.items():
            if len(pool) < MIN_GROUP_SIZE:
                continue  # already in audit.excluded with a named reason
            result = METHODS[name](pool, seed, key)
            outcome.pool_results.append(result)
            outcome.unmatched.update(result.unmatched)
        outcome.seconds = time.perf_counter() - start
        run.methods[name] = outcome
    return run
