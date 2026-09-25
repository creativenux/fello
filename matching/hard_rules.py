"""
hard_rules.py

Stage 1 of the matching method: hard-rule eligibility filtering.

  1. Adult eligibility: the lower bound of the age band must be >= 18.
     Always satisfied by the generator (youngest band is 18-29) but still
     checked and logged, so every rule is inspectable.
  2. Shared condition category.
  3. Shared communication language.
     Rules 2 and 3 partition the dataset into disjoint eligible pools; groups
     are only ever formed inside one pool.
  4. Group size 6 to 8 (plan_group_sizes).

Every exclusion carries a named, human-readable reason.

Author: Toheeb Olayemi (2516683), University of Chester.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from matching.attributes import MIN_GROUP_SIZE, MAX_GROUP_SIZE, TARGET_GROUP_SIZE, POOL_KEYS

ADULT_AGE = 18


# =============================================================================
# RULE 4: GROUP SIZE
# =============================================================================

@dataclass
class GroupSizePlan:
    sizes: list          # target size of each group, each in [6, 8]
    leftover: int        # profiles that cannot be placed without breaking [6, 8]
    reason: str = ""     # why there is a leftover, empty when leftover == 0


def plan_group_sizes(pool_size: int) -> GroupSizePlan:
    """Split a pool as evenly as possible into groups of 6 to 8.

    The number of groups is round(pool_size / 7), clamped to the feasible
    range [ceil(n/8), floor(n/6)]. When that range is empty (n < 6, or n in {9, 10, 11, 17}), as many groups of 8 as possible
    are formed and the remainder is reported, never forced into an invalid
    group. Rounding is half-up, not Python's banker's rounding.
    """
    n = pool_size
    if n < MIN_GROUP_SIZE:
        reason = f"pool_too_small: pool_size={n}, minimum_required={MIN_GROUP_SIZE}" if n else ""
        return GroupSizePlan([], n, reason)

    k = int(n / TARGET_GROUP_SIZE + 0.5)
    k_min = -(-n // MAX_GROUP_SIZE)
    k_max = n // MIN_GROUP_SIZE
    if k_min <= k_max:
        k = min(max(k, k_min), k_max)
        base, extra = divmod(n, k)
        sizes = [base + 1] * extra + [base] * (k - extra)
        return GroupSizePlan(sizes, 0)

    k = k_max
    leftover = n - k * MAX_GROUP_SIZE
    reason = (f"remainder_not_absorbable: pool_size={n} cannot be divided into groups "
              f"of {MIN_GROUP_SIZE} to {MAX_GROUP_SIZE}; {leftover} left over")
    return GroupSizePlan([MAX_GROUP_SIZE] * k, leftover, reason)


# =============================================================================
# RULES 1 TO 3: ELIGIBLE POOLS
# =============================================================================

@dataclass
class HardRuleAudit:
    rules: list = field(default_factory=list)     # one entry per rule
    pools: list = field(default_factory=list)     # one entry per pool
    excluded: dict = field(default_factory=dict)  # profile_id -> reason


def _band_lower_bound(band: str) -> int:
    return int(str(band).replace("+", "").split("-")[0])


def partition_into_eligible_pools(df: pd.DataFrame):
    """Partition profiles into eligible pools keyed by (condition_category, language).

    Returns (pools, audit). pools maps (primary_condition_category,
    communication_language) to the sub-DataFrame of eligible profiles sharing
    both. audit records every rule (including those that excluded no one),
    every pool's size and viability, and a named reason for every profile
    that cannot be grouped at this stage.
    """
    audit = HardRuleAudit()

    # Rule 1: adult eligibility.
    lower = df["age_band"].map(_band_lower_bound)
    not_adult = df[lower < ADULT_AGE]
    for pid, band in zip(not_adult["profile_id"], not_adult["age_band"]):
        audit.excluded[pid] = f"not_adult: age_band={band}, minimum_age={ADULT_AGE}"
    audit.rules.append({
        "rule": "adult_eligibility", "status": "applied",
        "checked": len(df), "excluded": len(not_adult),
        "note": "Every generated profile is an adult by construction; checked for audit completeness.",
    })
    adults = df[lower >= ADULT_AGE]

    # Rules 2 and 3: shared condition category and shared language. These
    # never exclude anyone by themselves; they decide who may be grouped
    # together.
    pools = {key: pool for key, pool in adults.groupby(list(POOL_KEYS), sort=True)}
    for rule in ("shared_condition_category", "shared_communication_language"):
        audit.rules.append({
            "rule": rule, "status": "applied", "checked": len(adults), "excluded": 0,
            "note": "Partitions profiles into pools; groups never cross pools.",
        })

    # Pool viability: a pool smaller than the minimum group size cannot form
    # even one group.
    for (category, language), pool in pools.items():
        viable = len(pool) >= MIN_GROUP_SIZE
        audit.pools.append({"category": category, "language": language,
                            "size": len(pool), "viable": viable})
        if not viable:
            reason = (f"pool_too_small: category={category}, language={language}, "
                      f"pool_size={len(pool)}, minimum_required={MIN_GROUP_SIZE}")
            for pid in pool["profile_id"]:
                audit.excluded[pid] = reason
    audit.rules.append({
        "rule": "group_size", "status": "applied", "checked": len(adults),
        "excluded": sum(p["size"] for p in audit.pools if not p["viable"]),
        "note": f"Groups must have {MIN_GROUP_SIZE} to {MAX_GROUP_SIZE} members.",
    })
    return pools, audit
