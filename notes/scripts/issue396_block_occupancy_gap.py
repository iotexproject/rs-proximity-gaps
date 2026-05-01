"""Block-occupancy audit for issue #396 saturated components.

The current dyadic closure explains components that contain a full cyclotomic
block C_r: two-block components contain two full blocks, and one-substitution
near components contain one full block.  This script isolates the remaining
hard obstruction by checking whether any non-full saturated component in the
current panels has no full block.
"""

from __future__ import annotations

import os
import sys
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from issue396_action_stabilizer import residual_uv
from issue396_component_family_scan import (
    precompute_component_tests,
    saturated_component_indices_fast,
)
from issue396_component_polynomial_audit import subgroup
from issue396_saturated_witness_general_k import (
    PANEL_64_3POS,
    PANEL_64_4POS,
    stable_coefs,
)


def occupancy(S):
    counts = [0, 0, 0, 0]
    for i in S:
        counts[i % 4] += 1
    return tuple(counts)


def analyze_support(support, p, tests):
    n2 = 16
    full_count = 12870
    coefs = stable_coefs(support, p)
    row_hist = Counter()
    component_occ = Counter()
    no_full_examples = []

    for alpha1 in range(p):
        u, v = residual_uv(support, coefs, alpha1, p, n2)
        indices = saturated_component_indices_fast(u, v, tests, p)
        if len(indices) == full_count:
            row_hist["full-row"] += 1
            continue
        if len(indices) == 0:
            row_hist["empty-row"] += 1
            continue
        row_hist["nonfull-nonempty"] += 1
        for idx in indices:
            S = tests["subsets"][int(idx)]
            occ = occupancy(S)
            component_occ[occ] += 1
            if max(occ) < 4 and len(no_full_examples) < 5:
                no_full_examples.append((alpha1, S, occ))
    return row_hist, component_occ, no_full_examples


def fmt_counter(counter):
    return "{" + ", ".join(f"{k}:{counter[k]}" for k in sorted(counter)) + "}"


def main():
    p = 193
    L2 = subgroup(16, p)
    tests = precompute_component_tests(L2, p)
    panels = [("3pos-known", PANEL_64_3POS), ("4pos-probes", PANEL_64_4POS)]

    print("Issue #396 block-occupancy gap audit")
    print(f"q={p}, L2=(16,4)")
    print("Non-full components are audited by occupancy across the four residue classes mod 4.")
    print()

    grand_rows = Counter()
    grand_occ = Counter()
    grand_no_full = []
    for panel, supports in panels:
        print(f"=== {panel} ===")
        panel_rows = Counter()
        panel_occ = Counter()
        for support in supports:
            rows, occ, examples = analyze_support(support, p, tests)
            panel_rows.update(rows)
            panel_occ.update(occ)
            grand_rows.update(rows)
            grand_occ.update(occ)
            grand_no_full.extend((support,) + ex for ex in examples)
            print(
                f"sup={support} mod4={tuple(j % 4 for j in support)} "
                f"rows={fmt_counter(rows)} occ={fmt_counter(occ)}"
            )
        print(f"panel_rows={fmt_counter(panel_rows)}")
        print(f"panel_occ={fmt_counter(panel_occ)}")
        print()

    print(f"grand_rows={fmt_counter(grand_rows)}")
    print(f"grand_occ={fmt_counter(grand_occ)}")
    print(f"no_full_component_examples={grand_no_full[:5]}")
    if grand_no_full:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
