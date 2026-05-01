"""Audit all-rho boundary certificates for ConjE exact half-set incidence.

An all-rho half-set S has both high vectors A_S and B_S equal to zero, so
rho*z^a + z^b agrees with degree < k on S for every rho.  The expected G3
boundary route is that, at deployment-shaped scales, these all-rho witnesses
are exactly the two parity half-cosets of L_n:

    {omega^i : i even}, {omega^i : i odd}.

On such a half-coset, exponents reduce modulo n/2.  Therefore z^e restricts to
degree < k iff e mod (n/2) < k.
"""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
from math import isqrt

from g3_conjE_cached_pair_sweep import classify_vectors, high_vectors_for_halfset
from g3_conjE_exact_halfset import subgroup


def parity_halfsets(n: int) -> set[tuple[int, ...]]:
    return {tuple(range(parity, n, 2)) for parity in (0, 1)}


def boundary_condition(n: int, k: int, a: int, b: int) -> bool:
    half = n // 2
    return (a % half) < k and (b % half) < k


def audit(n: int, k: int, q: int) -> list[dict[str, object]]:
    t = isqrt(k * n)
    if t * t != k * n:
        raise ValueError(f"sqrt(k*n) is not integral for n={n}, k={k}")
    L = subgroup(q, n)
    parity = parity_halfsets(n)
    pairs = [(a, b) for a in range(k, n) for b in range(a + 1, n)]
    exponents = sorted({e for pair in pairs for e in pair})
    degenerate: dict[tuple[int, int], list[tuple[int, ...]]] = {pair: [] for pair in pairs}
    for indices in combinations(range(n), t):
        points = [L[i] for i in indices]
        vectors = high_vectors_for_halfset(points, exponents, k, t, q)
        for pair in pairs:
            a, b = pair
            kind, _rho = classify_vectors(vectors[a], vectors[b], q)
            if kind == "all":
                degenerate[pair].append(tuple(indices))

    rows = []
    for (a, b), degenerate_sets in degenerate.items():
        if not degenerate_sets:
            continue
        rows.append(
            {
                "a": a,
                    "b": b,
                    "degenerate": len(degenerate_sets),
                    "all_parity": all(indices in parity for indices in degenerate_sets),
                    "boundary_condition": boundary_condition(n, k, a, b),
                    "sets": degenerate_sets,
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument("--q", type=int, default=97)
    args = parser.parse_args()

    k = args.k if args.k is not None else args.n // 4
    rows = audit(args.n, k, args.q)
    summary = Counter(
        (row["all_parity"], row["boundary_condition"], row["degenerate"]) for row in rows
    )
    print(f"boundary all-rho audit n={args.n} k={k} q={args.q}")
    print(f"pairs_with_allrho={len(rows)}")
    print(f"summary={dict(summary)}")
    for row in rows:
        print(
            f"  (a,b)=({row['a']},{row['b']}) "
            f"degenerate={row['degenerate']} all_parity={row['all_parity']} "
            f"boundary_condition={row['boundary_condition']} sets={row['sets']}"
        )


if __name__ == "__main__":
    main()
