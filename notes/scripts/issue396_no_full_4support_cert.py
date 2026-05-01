"""Issue #396 no-full certifier for low-support true multi-term layers.

The strict three-support branch is closed by Note 0337 because every mixed
case has a singleton residual side.  The next irreducible case is a four
support with two exponents on each alpha2 side.  Higher support sizes can be
scanned by the same linear-alpha mechanism.  For a fixed support and 8-subset
S of L2=(16,4), saturation is still linear in alpha1:

    C(S) + alpha1 M(S) = 0.

This script scans those linear systems over a support window and asks whether
any no-full saturated component survives with primitive rank two after
requiring at least two terms on both alpha2 sides.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from itertools import combinations
from multiprocessing import Pool

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


_P = None
_N2 = None
_K2 = None
_TAILS = None
_SUBSETS = None
_OMEGA2 = None
_SIDE_MIN = None


def support_side_counts(support):
    u = sum((j % 4) < 2 for j in support)
    return u, len(support) - u


def init_worker(p, n2, k2, side_min):
    global _P, _N2, _K2, _TAILS, _SUBSETS, _OMEGA2, _SIDE_MIN
    _P = p
    _N2 = n2
    _K2 = k2
    _SIDE_MIN = side_min
    _OMEGA2 = find_prim_root(p, n2)
    if _OMEGA2 is None:
        raise ValueError(f"F_{p} has no primitive {n2}-th root")

    import issue396_no_full_symbolic_cert as cert

    cert.init_worker(p, n2, k2)
    L2 = subgroup(n2, p)
    tests = precompute_component_tests(L2, p)
    keep = [i for i, S in enumerate(tests["subsets"]) if max(occupancy(S)) < k2]
    _TAILS = tests["tails"][keep]
    _SUBSETS = tuple(tests["subsets"][i] for i in keep)


def row_class(support, coefs, alpha1):
    u, v = residual_uv(support, coefs, alpha1, _P, _N2)
    if row_rank(u, v) < 2:
        return "rank<2"
    if all((c % _P) == 0 for c in u[_K2:]) and all((c % _P) == 0 for c in v[_K2:]):
        return "full"
    if len(stabilizer_exponents(u, v, _OMEGA2, _P)) > 1:
        return "stabilizer"
    return "primitive"


def scan_support(support):
    hist = Counter()
    side = support_side_counts(support)
    if min(side) < _SIDE_MIN:
        hist[f"side:{side}"] += 1
        return {"hist": hist}

    hist[f"side:{side}"] += 1
    coefs = stable_coefs(support, _P)
    u0, u1, v0, v1 = split_residual_linear_parts(support, coefs)
    cu = np.tensordot(_TAILS, u0, axes=([1], [0])) % _P
    su = np.tensordot(_TAILS, u1, axes=([1], [0])) % _P
    cv = np.tensordot(_TAILS, v0, axes=([1], [0])) % _P
    sv = np.tensordot(_TAILS, v1, axes=([1], [0])) % _P
    constants = np.concatenate([cu, cv], axis=1)
    slopes = np.concatenate([su, sv], axis=1)
    idx, alpha, all_alpha = candidate_rows(constants, slopes)

    hist["candidate_subsets"] += int(len(idx))
    hist["all_alpha_subsets"] += int(len(all_alpha))

    for subset_idx, alpha1 in zip(idx, alpha):
        alpha1 = int(alpha1)
        if alpha1 == 0:
            hist["alpha_zero"] += 1
            continue
        cls = row_class(support, coefs, alpha1)
        hist[f"class:{cls}"] += 1
        if cls == "primitive":
            S = _SUBSETS[int(subset_idx)]
            return {
                "hist": hist,
                "counterexample": {
                    "support": support,
                    "coefs": tuple(int(c % _P) for c in coefs),
                    "alpha1": alpha1,
                    "S": S,
                    "occupancy": occupancy(S),
                },
            }

    if len(all_alpha):
        for alpha1 in range(1, _P):
            cls = row_class(support, coefs, alpha1)
            hist[f"all-alpha-class:{cls}"] += len(all_alpha)
            if cls == "primitive":
                S = _SUBSETS[int(all_alpha[0])]
                return {
                    "hist": hist,
                    "counterexample": {
                        "support": support,
                        "coefs": tuple(int(c % _P) for c in coefs),
                        "alpha1": alpha1,
                        "S": S,
                        "occupancy": occupancy(S),
                        "all_alpha": True,
                    },
                }
            break

    return {"hist": hist}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, required=True)
    parser.add_argument("--n2", type=int, default=16)
    parser.add_argument("--k2", type=int, default=4)
    parser.add_argument("--support-start", type=int, default=16)
    parser.add_argument("--support-count", type=int, default=48)
    parser.add_argument("--support-size", type=int, default=4)
    parser.add_argument("--side-min", type=int, default=2)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--chunksize", type=int, default=16)
    parser.add_argument("--progress", type=int, default=2000)
    return parser.parse_args()


def main():
    args = parse_args()
    support_stop = args.support_start + args.support_count
    supports = list(combinations(range(args.support_start, support_stop), args.support_size))
    print(f"Issue #396 no-full {args.support_size}-support bilateral certifier")
    print(
        f"q={args.q}, L2=({args.n2},{args.k2}), "
        f"support_window=[{args.support_start},{support_stop}), "
        f"supports=C({args.support_count},{args.support_size})={len(supports)}, "
        f"side_min={args.side_min}, workers={args.workers}"
    )
    print()

    hist = Counter()
    first = None
    done = 0
    with Pool(
        processes=args.workers,
        initializer=init_worker,
        initargs=(args.q, args.n2, args.k2, args.side_min),
    ) as pool:
        for result in pool.imap_unordered(scan_support, supports, chunksize=args.chunksize):
            done += 1
            hist["supports"] += 1
            hist.update(result["hist"])
            if result.get("counterexample") is not None:
                hist["counterexample_supports"] += 1
                first = result["counterexample"]
                pool.terminate()
                break
            if args.progress and done % args.progress == 0:
                print(f"progress supports={done}", flush=True)

    print()
    print(f"hist={dict(sorted(hist.items()))}")
    print(f"first_counterexample={first}")
    if first is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
