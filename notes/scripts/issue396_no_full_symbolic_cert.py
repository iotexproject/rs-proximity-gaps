"""Symbolic-alpha certifier for issue #396 primitive no-full components.

For a fixed strict-above-J 3-support and an 8-subset S of L2=(16,4), the
condition that both residual basis vectors u_alpha and v_alpha lie in RS_4(S)
is linear in alpha1:

    C(S) + alpha1 * M(S) = 0.

This script solves those linear equations directly instead of enumerating all
alpha1 in F_q.  It certifies the corrected primitive rank-2 claim from
Note 0325: no saturated no-full-block component appears after excluding
rank-0/rank-1 rows.
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
from issue396_saturated_witness_general_k import stable_coefs


_P = None
_N2 = None
_K2 = None
_TAILS = None
_SUBSETS = None
_INV = None
_OMEGA2 = None


def occupancy(S):
    counts = [0, 0, 0, 0]
    for i in S:
        counts[i % 4] += 1
    return tuple(counts)


def init_worker(p, n2, k2):
    global _P, _N2, _K2, _TAILS, _SUBSETS, _INV, _OMEGA2
    _P = p
    _N2 = n2
    _K2 = k2
    inv = np.zeros(p, dtype=np.int64)
    for a in range(1, p):
        inv[a] = pow(a, p - 2, p)
    _INV = inv

    _OMEGA2 = find_prim_root(p, n2)
    if _OMEGA2 is None:
        raise ValueError(f"F_{p} has no primitive {n2}-th root")
    L2 = subgroup(n2, p)
    tests = precompute_component_tests(L2, p)
    keep = [i for i, S in enumerate(tests["subsets"]) if max(occupancy(S)) < k2]
    _TAILS = tests["tails"][keep]
    _SUBSETS = tuple(tests["subsets"][i] for i in keep)


def split_residual_linear_parts(support, coefs):
    u0 = np.zeros(_N2, dtype=np.int64)
    u1 = np.zeros(_N2, dtype=np.int64)
    v0 = np.zeros(_N2, dtype=np.int64)
    v1 = np.zeros(_N2, dtype=np.int64)
    for j, c in zip(support, coefs):
        r = (j // 4) % _N2
        c %= _P
        q = j % 4
        if q == 0:
            u0[r] = (u0[r] + c) % _P
        elif q == 1:
            u1[r] = (u1[r] + c) % _P
        elif q == 2:
            v0[r] = (v0[r] + c) % _P
        else:
            v1[r] = (v1[r] + c) % _P
    return u0, u1, v0, v1


def row_rank(u, v):
    u_nz = any(c % _P for c in u)
    v_nz = any(c % _P for c in v)
    if not u_nz and not v_nz:
        return 0
    if not u_nz or not v_nz:
        return 1
    ratio = None
    for a, b in zip(u, v):
        a %= _P
        b %= _P
        if b == 0:
            if a != 0:
                return 2
            continue
        r = a * pow(b, _P - 2, _P) % _P
        if ratio is None:
            ratio = r
        elif ratio != r:
            return 2
    return 1


def is_full_row(u, v):
    return all((c % _P) == 0 for c in u[_K2:]) and all((c % _P) == 0 for c in v[_K2:])


def alpha_class(support, coefs, alpha1):
    u, v = residual_uv(support, coefs, alpha1, _P, _N2)
    if row_rank(u, v) < 2:
        return "rank<2"
    if is_full_row(u, v):
        return "full"
    if len(stabilizer_exponents(u, v, _OMEGA2, _P)) > 1:
        return "stabilizer"
    return "primitive"


def first_primitive_alpha(support, coefs):
    for alpha1 in range(_P):
        if alpha_class(support, coefs, alpha1) == "primitive":
            return alpha1
    return None


def candidate_rows(constants, slopes):
    nonzero_slope = slopes != 0
    has_slope = np.any(nonzero_slope, axis=1)
    all_zero = np.all(constants == 0, axis=1) & ~has_slope

    idx = np.flatnonzero(has_slope)
    if len(idx) == 0:
        return np.array([], dtype=np.int64), np.array([], dtype=np.int64), np.flatnonzero(all_zero)

    first = np.argmax(nonzero_slope[idx], axis=1)
    c0 = constants[idx, first]
    s0 = slopes[idx, first]
    alpha = ((-c0 % _P) * _INV[s0]) % _P
    ok = np.all((constants[idx] + alpha[:, None] * slopes[idx]) % _P == 0, axis=1)
    return idx[ok], alpha[ok], np.flatnonzero(all_zero)


def scan_support(support):
    coefs = stable_coefs(support, _P)
    u0, u1, v0, v1 = split_residual_linear_parts(support, coefs)

    cu = np.tensordot(_TAILS, u0, axes=([1], [0])) % _P
    su = np.tensordot(_TAILS, u1, axes=([1], [0])) % _P
    cv = np.tensordot(_TAILS, v0, axes=([1], [0])) % _P
    sv = np.tensordot(_TAILS, v1, axes=([1], [0])) % _P
    constants = np.concatenate([cu, cv], axis=1)
    slopes = np.concatenate([su, sv], axis=1)

    idx, alpha, all_alpha = candidate_rows(constants, slopes)
    checked_candidates = 0
    candidate_classes = Counter()
    for subset_idx, alpha1 in zip(idx, alpha):
        checked_candidates += 1
        alpha1 = int(alpha1)
        cls = alpha_class(support, coefs, alpha1)
        candidate_classes[cls] += 1
        if cls == "primitive":
            S = _SUBSETS[int(subset_idx)]
            return {
                "support": support,
                "alpha1": alpha1,
                "rank": 2,
                "S": S,
                "occupancy": occupancy(S),
                "candidate_subsets": int(len(idx)),
                "all_alpha_subsets": int(len(all_alpha)),
                "candidate_classes": dict(candidate_classes),
            }

    all_alpha_primitive = None
    if len(all_alpha):
        all_alpha_primitive = first_primitive_alpha(support, coefs)
        if all_alpha_primitive is not None:
            S = _SUBSETS[int(all_alpha[0])]
            return {
                "support": support,
                "alpha1": all_alpha_primitive,
                "rank": 2,
                "S": S,
                "occupancy": occupancy(S),
                "candidate_subsets": int(len(idx)),
                "all_alpha_subsets": int(len(all_alpha)),
            }

    return {
        "support": support,
        "candidate_subsets": int(len(idx)),
        "all_alpha_subsets": int(len(all_alpha)),
        "checked_candidates": checked_candidates,
        "candidate_classes": dict(candidate_classes),
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, required=True)
    parser.add_argument("--n2", type=int, default=16)
    parser.add_argument("--k2", type=int, default=4)
    parser.add_argument("--support-start", type=int, default=16)
    parser.add_argument("--support-count", type=int, default=48)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--chunksize", type=int, default=16)
    return parser.parse_args()


def main():
    args = parse_args()
    support_stop = args.support_start + args.support_count
    supports = list(combinations(range(args.support_start, support_stop), 3))
    print("Issue #396 symbolic-alpha no-full primitive rank-2 certifier")
    print(
        f"q={args.q}, L2=({args.n2},{args.k2}), "
        f"support_window=[{args.support_start},{support_stop}), "
        f"supports=C({args.support_count},3)={len(supports)}, workers={args.workers}"
    )
    print()

    hist = Counter()
    first = None
    done = 0
    with Pool(
        processes=args.workers,
        initializer=init_worker,
        initargs=(args.q, args.n2, args.k2),
    ) as pool:
        for r in pool.imap_unordered(scan_support, supports, chunksize=args.chunksize):
            done += 1
            hist["supports"] += 1
            hist["candidate_subsets"] += r.get("candidate_subsets", 0)
            hist["all_alpha_subsets"] += r.get("all_alpha_subsets", 0)
            for cls, count in r.get("candidate_classes", {}).items():
                hist[f"class:{cls}"] += count
            if "alpha1" in r:
                hist["counterexample_supports"] += 1
                first = r
                pool.terminate()
                break
            if done % 1000 == 0:
                print(f"progress supports={done}", flush=True)

    print()
    print(f"hist={dict(sorted(hist.items()))}")
    print(f"first_counterexample={first}")
    if first is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
