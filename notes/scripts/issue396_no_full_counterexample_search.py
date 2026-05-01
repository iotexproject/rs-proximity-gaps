"""Search for no-full-block saturated components in all 3-position supports.

This targets the exact remaining gap from Note 0324.  At (64,16)->L2=(16,4),
scan every 3-position Fourier support in the strict above-Johnson window
{16,...,63}.  For each support and every alpha1 in F_193, test only the
8-subsets S whose occupancy across the four cyclotomic blocks is <4 in every
block.  Full-code rows are skipped.

If such an S exists, the Note 0324 no-full-block exclusion is false already at
the first deployment toy scale.  Set ISSUE396_SKIP_RANK1=1 to continue the
search after excluding rank-0/rank-1 rows, which targets the corrected
primitive rank-2 version from Note 0325.
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

from issue396_action_stabilizer import residual_uv
from issue396_component_family_scan import precompute_component_tests
from issue396_component_polynomial_audit import subgroup
from issue396_saturated_witness_general_k import stable_coefs


_P = None
_N2 = None
_K2 = None
_TAILS = None
_SUBSETS = None
_SKIP_RANK1 = False


def occupancy(S):
    counts = [0, 0, 0, 0]
    for i in S:
        counts[i % 4] += 1
    return tuple(counts)


def init_worker(p, n2, k2, skip_rank1):
    global _P, _N2, _K2, _TAILS, _SUBSETS, _SKIP_RANK1
    _P = p
    _N2 = n2
    _K2 = k2
    _SKIP_RANK1 = skip_rank1
    L2 = subgroup(n2, p)
    tests = precompute_component_tests(L2, p)
    keep = [i for i, S in enumerate(tests["subsets"]) if max(occupancy(S)) < k2]
    _TAILS = tests["tails"][keep]
    _SUBSETS = tuple(tests["subsets"][i] for i in keep)


def nofull_indices(u_coeff, v_coeff):
    tails = _TAILS
    u = np.array([(c % _P) for c in u_coeff[:_N2]], dtype=np.int64)
    v = np.array([(c % _P) for c in v_coeff[:_N2]], dtype=np.int64)
    u_acc = np.tensordot(tails, u, axes=([1], [0])) % _P
    v_acc = np.tensordot(tails, v, axes=([1], [0])) % _P
    mask = np.all(u_acc == 0, axis=1) & np.all(v_acc == 0, axis=1)
    return np.flatnonzero(mask)


def is_full_row(u, v):
    return all((c % _P) == 0 for c in u[_K2:]) and all((c % _P) == 0 for c in v[_K2:])


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


def scan_support(support):
    coefs = stable_coefs(support, _P)
    full_rows = 0
    skipped_rank1 = 0
    for alpha1 in range(_P):
        u, v = residual_uv(support, coefs, alpha1, _P, _N2)
        rank = row_rank(u, v)
        if _SKIP_RANK1 and rank < 2:
            skipped_rank1 += 1
            continue
        if is_full_row(u, v):
            full_rows += 1
            continue
        idx = nofull_indices(u, v)
        if len(idx):
            examples = []
            for i in idx[:5]:
                S = _SUBSETS[int(i)]
                examples.append((S, occupancy(S)))
            return {
                "support": support,
                "alpha1": alpha1,
                "rank": rank,
                "examples": examples,
                "full_rows": full_rows,
                "skipped_rank1": skipped_rank1,
            }
    return {"support": support, "full_rows": full_rows, "skipped_rank1": skipped_rank1}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, default=int(os.environ.get("ISSUE396_Q", "193")))
    parser.add_argument("--n2", type=int, default=int(os.environ.get("ISSUE396_N2", "16")))
    parser.add_argument("--k2", type=int, default=int(os.environ.get("ISSUE396_K2", "4")))
    parser.add_argument(
        "--support-start",
        type=int,
        default=int(os.environ.get("ISSUE396_SUPPORT_START", "16")),
    )
    parser.add_argument(
        "--support-count",
        type=int,
        default=int(os.environ.get("ISSUE396_SUPPORT_COUNT", "48")),
    )
    parser.add_argument("--workers", type=int, default=int(os.environ.get("ISSUE396_WORKERS", "12")))
    parser.add_argument("--chunksize", type=int, default=int(os.environ.get("ISSUE396_CHUNKSIZE", "8")))
    parser.add_argument(
        "--skip-rank1",
        action="store_true",
        default=os.environ.get("ISSUE396_SKIP_RANK1", "0") == "1",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    support_stop = args.support_start + args.support_count
    supports = list(combinations(range(args.support_start, support_stop), 3))
    print("Issue #396 no-full-block counterexample search")
    print(
        f"q={args.q}, L2=({args.n2},{args.k2}), "
        f"support_window=[{args.support_start},{support_stop}), "
        f"supports=C({args.support_count},3)={len(supports)}, workers={args.workers}"
    )
    print(f"Scanning all alpha1; full-code rows are skipped; skip_rank1={args.skip_rank1}.")
    print()

    hist = Counter()
    first = None
    done = 0
    with Pool(
        processes=args.workers,
        initializer=init_worker,
        initargs=(args.q, args.n2, args.k2, args.skip_rank1),
    ) as pool:
        for r in pool.imap_unordered(scan_support, supports, chunksize=args.chunksize):
            done += 1
            hist["supports"] += 1
            hist["full_rows"] += r.get("full_rows", 0)
            hist["skipped_rank1"] += r.get("skipped_rank1", 0)
            if "alpha1" in r:
                hist["counterexample_supports"] += 1
                if first is None:
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
