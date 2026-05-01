"""Pattern audit for issue #396 symbolic no-full candidates.

The symbolic-alpha certifier proves a large finite panel but does not explain
why every legal no-full candidate collapses in rank.  This script keeps the
same equations and aggregates the candidates by:

  - support fold quadrants j mod 4;
  - residual L2 exponent multiplicities floor(j/4) mod n2;
  - no-full component occupancy modulo the four quarter blocks;
  - rank-collapse mechanism.

The output is meant to identify finite proof cases for the primitive
rank-2/no-full exclusion.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from fri_2round_attack import find_prim_root
from issue396_action_stabilizer import residual_uv, stabilizer_exponents
from issue396_component_family_scan import precompute_component_tests
from issue396_component_polynomial_audit import subgroup
from issue396_no_full_symbolic_cert import (
    candidate_rows,
    occupancy,
    row_rank,
    split_residual_linear_parts,
)
from issue396_saturated_witness_general_k import stable_coefs


def support_signature(support, n2):
    quadrants = tuple(j % 4 for j in support)
    exps = tuple((j // 4) % n2 for j in support)
    exp_hist = tuple(sorted(Counter(exps).values(), reverse=True))
    uv_counts = (sum(q < 2 for q in quadrants), sum(q >= 2 for q in quadrants))
    return quadrants, exp_hist, uv_counts


def nonzero_positions(poly, p):
    return tuple(i for i, c in enumerate(poly) if c % p)


def rank_mechanism(u, v, p):
    su = nonzero_positions(u, p)
    sv = nonzero_positions(v, p)
    if not su and not sv:
        return "zero-row"
    if not su:
        return f"u=0/v{len(sv)}"
    if not sv:
        return f"v=0/u{len(su)}"
    if su != sv:
        return f"dependent-different-supports:u{len(su)}v{len(sv)}"
    return f"dependent-same-support:{len(su)}"


def alpha_class_and_mechanism(support, coefs, alpha1, p, n2, k2, omega2):
    u, v = residual_uv(support, coefs, alpha1, p, n2)
    if row_rank(u, v) < 2:
        return "rank<2", rank_mechanism(u, v, p)
    if all((c % p) == 0 for c in u[k2:]) and all((c % p) == 0 for c in v[k2:]):
        return "full", "full"
    if len(stabilizer_exponents(u, v, omega2, p)) > 1:
        return "stabilizer", str(stabilizer_exponents(u, v, omega2, p))
    return "primitive", "primitive"


def audit(args):
    p = args.q
    n2 = args.n2
    k2 = args.k2
    omega2 = find_prim_root(p, n2)
    if omega2 is None:
        raise ValueError(f"F_{p} has no primitive {n2}-th root")

    # Initialize the globals used by the imported vectorized helpers.
    import issue396_no_full_symbolic_cert as cert

    cert.init_worker(p, n2, k2)

    L2 = subgroup(n2, p)
    tests = precompute_component_tests(L2, p)
    keep = [i for i, S in enumerate(tests["subsets"]) if max(occupancy(S)) < k2]
    tails = tests["tails"][keep]
    subsets = tuple(tests["subsets"][i] for i in keep)

    support_stop = args.support_start + args.support_count
    supports = list(combinations(range(args.support_start, support_stop), 3))

    class_hist = Counter()
    support_key_hist = Counter()
    occupancy_hist = Counter()
    mechanism_hist = Counter()
    joint_hist = Counter()
    examples = {}
    mechanism_examples = {}

    for done, support in enumerate(supports, 1):
        coefs = stable_coefs(support, p)
        u0, u1, v0, v1 = split_residual_linear_parts(support, coefs)
        cu = np.tensordot(tails, u0, axes=([1], [0])) % p
        su = np.tensordot(tails, u1, axes=([1], [0])) % p
        cv = np.tensordot(tails, v0, axes=([1], [0])) % p
        sv = np.tensordot(tails, v1, axes=([1], [0])) % p
        constants = np.concatenate([cu, cv], axis=1)
        slopes = np.concatenate([su, sv], axis=1)
        idx, alpha, all_alpha = candidate_rows(constants, slopes)

        sig = support_signature(support, n2)
        candidate_total = len(idx) + len(all_alpha)
        if candidate_total:
            support_key_hist[sig] += candidate_total
        for subset_idx, alpha1 in zip(idx, alpha):
            S = subsets[int(subset_idx)]
            occ = occupancy(S)
            alpha1 = int(alpha1)
            cls, mech = alpha_class_and_mechanism(
                support, coefs, alpha1, p, n2, k2, omega2
            )
            class_hist[cls] += 1
            occupancy_hist[(cls, occ)] += 1
            mechanism_hist[(cls, mech)] += 1
            joint = (sig, occ, cls, mech)
            joint_hist[joint] += 1
            examples.setdefault(
                joint,
                {
                    "support": support,
                    "alpha1": alpha1,
                    "S": S,
                    "coefs": tuple(c % p for c in coefs),
                },
            )
            mechanism_examples.setdefault(
                (cls, mech),
                {
                    "support": support,
                    "alpha1": alpha1,
                    "S": S,
                    "occupancy": occ,
                    "support_signature": sig,
                    "coefs": tuple(c % p for c in coefs),
                },
            )

        if len(all_alpha):
            # all-alpha no-full equations are rare and dangerous; classify one
            # representative alpha from each row class.
            for alpha1 in range(p):
                cls, mech = alpha_class_and_mechanism(
                    support, coefs, alpha1, p, n2, k2, omega2
                )
                class_hist[f"all-alpha:{cls}"] += len(all_alpha)
                occ = occupancy(subsets[int(all_alpha[0])])
                mechanism_hist[(f"all-alpha:{cls}", mech)] += len(all_alpha)
                examples.setdefault(
                    (sig, occ, f"all-alpha:{cls}", mech),
                    {
                        "support": support,
                        "alpha1": alpha1,
                        "S": subsets[int(all_alpha[0])],
                        "coefs": tuple(c % p for c in coefs),
                    },
                )
                mechanism_examples.setdefault(
                    (f"all-alpha:{cls}", mech),
                    {
                        "support": support,
                        "alpha1": alpha1,
                        "S": subsets[int(all_alpha[0])],
                        "occupancy": occ,
                        "support_signature": sig,
                        "coefs": tuple(c % p for c in coefs),
                    },
                )
                break

        if args.progress and done % args.progress == 0:
            print(f"progress supports={done}", flush=True)

    return {
        "supports": len(supports),
        "class_hist": class_hist,
        "support_key_hist": support_key_hist,
        "occupancy_hist": occupancy_hist,
        "mechanism_hist": mechanism_hist,
        "joint_hist": joint_hist,
        "examples": examples,
        "mechanism_examples": mechanism_examples,
    }


def fmt_counter(counter, limit=None):
    items = counter.most_common(limit)
    return "\n".join(f"  {k}: {v}" for k, v in items)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, default=193)
    parser.add_argument("--n2", type=int, default=16)
    parser.add_argument("--k2", type=int, default=4)
    parser.add_argument("--support-start", type=int, default=16)
    parser.add_argument("--support-count", type=int, default=48)
    parser.add_argument("--progress", type=int, default=1000)
    parser.add_argument("--top", type=int, default=30)
    return parser.parse_args()


def main():
    args = parse_args()
    result = audit(args)
    print("Issue #396 no-full symbolic pattern audit")
    print(
        f"q={args.q}, L2=({args.n2},{args.k2}), "
        f"support_window=[{args.support_start},{args.support_start + args.support_count}), "
        f"supports={result['supports']}"
    )
    print()
    print("class_hist:")
    print(fmt_counter(result["class_hist"], args.top))
    print()
    print("mechanism_hist:")
    print(fmt_counter(result["mechanism_hist"], args.top))
    print()
    print("mechanism_examples:")
    for key, ex in result["mechanism_examples"].items():
        print(f"  {key}: {ex}")
    print()
    print("occupancy_hist:")
    print(fmt_counter(result["occupancy_hist"], args.top))
    print()
    print("support_key_hist:")
    print(fmt_counter(result["support_key_hist"], args.top))
    print()
    print("joint_hist:")
    print(fmt_counter(result["joint_hist"], args.top))
    print()
    print("examples:")
    for key, ex in list(result["examples"].items())[: args.top]:
        print(f"  {key}: {ex}")


if __name__ == "__main__":
    main()
