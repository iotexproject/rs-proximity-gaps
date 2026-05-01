"""Audit the support-side geometry of issue #396 no-full saturation cases.

The GB certificate proves emptiness after quotienting alpha1=0 and saturating
away u=0 and v=0.  This script checks the simpler structural explanation:
whether every surviving no-full symbolic-alpha case before the final
saturations already has its 3-support entirely on one alpha2 side.

If all support exponents have j mod 4 in {0,1}, then v_alpha is identically
zero.  If all have j mod 4 in {2,3}, then u_alpha is identically zero.  Either
case is rank-one before any component-specific algebra.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from itertools import combinations

import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from issue396_component_family_scan import precompute_component_tests
from issue396_component_polynomial_audit import subgroup
from issue396_no_full_symbolic_cert import (
    candidate_rows,
    occupancy,
    split_residual_linear_parts,
)
from issue396_saturated_witness_general_k import stable_coefs


def side_key(support):
    quadrants = tuple(j % 4 for j in support)
    u_side = sum(q < 2 for q in quadrants)
    v_side = len(quadrants) - u_side
    return quadrants, (u_side, v_side)


def audit_prime(q, args):
    import issue396_no_full_symbolic_cert as cert

    cert.init_worker(q, args.n2, args.k2)

    L2 = subgroup(args.n2, q)
    tests = precompute_component_tests(L2, q)
    keep = [i for i, S in enumerate(tests["subsets"]) if max(occupancy(S)) < args.k2]
    tails = tests["tails"][keep]

    support_stop = args.support_start + args.support_count
    supports = combinations(range(args.support_start, support_stop), 3)

    hist = Counter()
    side_hist = Counter()
    quadrant_hist = Counter()
    alpha_kind_hist = Counter()
    first_mixed = None

    for support in supports:
        hist["supports"] += 1
        coefs = stable_coefs(support, q)
        u0, u1, v0, v1 = split_residual_linear_parts(support, coefs)
        cu = np.tensordot(tails, u0, axes=([1], [0])) % q
        su = np.tensordot(tails, u1, axes=([1], [0])) % q
        cv = np.tensordot(tails, v0, axes=([1], [0])) % q
        sv = np.tensordot(tails, v1, axes=([1], [0])) % q
        constants = np.concatenate([cu, cv], axis=1)
        slopes = np.concatenate([su, sv], axis=1)
        idx, alpha, all_alpha = candidate_rows(constants, slopes)

        hist["candidate_subsets"] += int(len(idx))
        hist["all_alpha_subsets"] += int(len(all_alpha))

        for alpha1 in alpha:
            if int(alpha1) == 0:
                hist["skipped_alpha_zero"] += 1
                continue
            hist["cases"] += 1
            alpha_kind_hist["point"] += 1
            quadrants, uv_counts = side_key(support)
            side_hist[uv_counts] += 1
            quadrant_hist[quadrants] += 1
            if uv_counts[0] and uv_counts[1] and first_mixed is None:
                first_mixed = {"support": support, "alpha1": int(alpha1)}

        for _subset_idx in all_alpha:
            hist["cases"] += 1
            alpha_kind_hist["all"] += 1
            quadrants, uv_counts = side_key(support)
            side_hist[uv_counts] += 1
            quadrant_hist[quadrants] += 1
            if uv_counts[0] and uv_counts[1] and first_mixed is None:
                first_mixed = {"support": support, "alpha1": "all"}

    return {
        "hist": hist,
        "cases": hist["cases"],
        "side_hist": side_hist,
        "quadrant_hist": quadrant_hist,
        "alpha_kind_hist": alpha_kind_hist,
        "first_mixed": first_mixed,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, action="append")
    parser.add_argument("--n2", type=int, default=16)
    parser.add_argument("--k2", type=int, default=4)
    parser.add_argument("--support-start", type=int, default=16)
    parser.add_argument("--support-count", type=int, default=48)
    parser.add_argument("--top", type=int, default=20)
    return parser.parse_args()


def main():
    args = parse_args()
    primes = args.q or [97, 193, 257, 449, 577, 769, 1153]
    print("Issue #396 no-full side-purity audit")
    print(
        f"L2=({args.n2},{args.k2}), "
        f"support_window=[{args.support_start},{args.support_start + args.support_count})"
    )
    print(flush=True)
    for q in primes:
        result = audit_prime(q, args)
        print(f"=== q={q} ===")
        print(f"hist={dict(sorted(result['hist'].items()))}")
        print(f"cases={result['cases']}")
        print(f"alpha_kind_hist={dict(sorted(result['alpha_kind_hist'].items()))}")
        print(f"side_hist={dict(sorted(result['side_hist'].items()))}")
        print("quadrant_hist:")
        for key, count in result["quadrant_hist"].most_common(args.top):
            print(f"  {key}: {count}")
        print(f"first_mixed={result['first_mixed']}")
        print(flush=True)
        if result["first_mixed"] is not None:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
