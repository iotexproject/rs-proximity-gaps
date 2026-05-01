"""Sweep Reverse/Pattern-B arising L2 exponent pairs for Conjecture E obstructions.

For Reverse supports with j mod 4 in {2,3}, the second fold contributes L2
exponents

    j = 4u+2  -> c exponent u
    j = 4u+3  -> d exponent u

When the resulting c/d union has two positions, the projective pencil is a
two-monomial pencil on L_{n2}.  This script lists those arising pairs and flags
the sign-paired obstruction |a-b| = n2/2 found by exact half-set incidence.
"""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
from math import gcd


def reverse_positions(n0: int, k0: int) -> list[int]:
    return [j for j in range(k0, n0) if j % 4 in (2, 3)]


def l2_position(j: int) -> int:
    if j % 4 == 2:
        return (j - 2) // 4
    if j % 4 == 3:
        return (j - 3) // 4
    raise ValueError(f"not a Reverse exponent: {j}")


def arising_pairs(n0: int, k0: int) -> Counter[tuple[int, int]]:
    pairs: Counter[tuple[int, int]] = Counter()
    for sup in combinations(reverse_positions(n0, k0), 3):
        pos = sorted({l2_position(j) for j in sup})
        if len(pos) == 2:
            pairs[(pos[0], pos[1])] += 1
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n0", type=int, required=True)
    parser.add_argument("--k0", type=int, default=None)
    args = parser.parse_args()

    k0 = args.k0 if args.k0 is not None else args.n0 // 4
    n2 = args.n0 // 4
    pairs = arising_pairs(args.n0, k0)

    flagged = []
    gcd_dist = Counter()
    for (a, b), multiplicity in pairs.items():
        diff = abs(a - b)
        g = gcd(diff, n2)
        gcd_dist[g] += multiplicity
        if diff == n2 // 2:
            flagged.append((a, b, multiplicity))

    print(f"n0={args.n0} k0={k0} n2={n2}")
    print(f"reverse_positions={len(reverse_positions(args.n0, k0))}")
    print(f"arising_two-position_pairs={len(pairs)}")
    print(f"gcd_distribution_by_support_multiplicity={sorted(gcd_dist.items())}")
    print(f"sign_paired_pair_count={len(flagged)}")
    for a, b, multiplicity in flagged[:80]:
        print(f"  pair=({a},{b}) diff={b-a} orbit_size={n2 // gcd(b-a, n2)} supports={multiplicity}")
    if len(flagged) > 80:
        print(f"  ... {len(flagged) - 80} more")


if __name__ == "__main__":
    main()
