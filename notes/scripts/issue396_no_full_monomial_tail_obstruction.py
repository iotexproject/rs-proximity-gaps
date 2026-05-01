"""Monomial-tail obstruction for issue #396 mixed no-full supports.

For a mixed alpha2-side 3-support, one side of the residual pencil has only a
single monomial.  Such a mixed support can satisfy a no-full component only if
that monomial lies in RS_4(S).  In the L2=(16,4) legal window, this means the
tail vector of x^e modulo g_S must vanish for some e in {4,...,15}.

This script verifies the finite obstruction:

    no-full S  =>  tail_S(x^e) != 0 for every e=4,...,15.

It is coefficient-free and does not use the stable random rows.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from issue396_component_family_scan import precompute_component_tests
from issue396_component_polynomial_audit import subgroup
from issue396_no_full_symbolic_cert import occupancy


def audit_prime(q: int, n2: int, k2: int, exp_start: int, exp_stop: int):
    L2 = subgroup(n2, q)
    tests = precompute_component_tests(L2, q)
    hist = Counter()
    first_bad = None
    occupancy_hist = Counter()
    exponents = range(exp_start, exp_stop)

    for S, tails in zip(tests["subsets"], tests["tails"]):
        occ = occupancy(S)
        if max(occ) >= k2:
            hist["full_block_subsets"] += 1
            continue
        hist["no_full_subsets"] += 1
        occupancy_hist[occ] += 1
        for e in exponents:
            if not any(int(x) % q for x in tails[e]):
                hist["zero_tail_monomials"] += 1
                if first_bad is None:
                    first_bad = {"S": S, "occupancy": occ, "e": e}

    return hist, occupancy_hist, first_bad


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, action="append")
    parser.add_argument("--n2", type=int, default=16)
    parser.add_argument("--k2", type=int, default=4)
    parser.add_argument("--exp-start", type=int, default=4)
    parser.add_argument("--exp-stop", type=int, default=16)
    parser.add_argument("--top", type=int, default=12)
    return parser.parse_args()


def main():
    args = parse_args()
    primes = args.q or [97, 193, 257, 449, 577, 769, 1153]
    print("Issue #396 no-full monomial-tail obstruction")
    print(f"L2=({args.n2},{args.k2}), exponents=[{args.exp_start},{args.exp_stop})")
    print()
    for q in primes:
        hist, occupancy_hist, first_bad = audit_prime(
            q, args.n2, args.k2, args.exp_start, args.exp_stop
        )
        print(f"=== q={q} ===")
        print(f"hist={dict(sorted(hist.items()))}")
        print("occupancy_hist:")
        for key, count in occupancy_hist.most_common(args.top):
            print(f"  {key}: {count}")
        print(f"first_bad={first_bad}")
        print()
        if first_bad is not None:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
