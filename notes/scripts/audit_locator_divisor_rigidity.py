"""Audit locator-divisor rigidity for ConjE certificate equations.

This enumerates degree-n/2 divisors P_S of x^n-1, applies the exact symbolic
high-vector equations by evaluating remainders modulo P_S, and reports whether
the surviving nonzero certificates are compatible with the action orbit or the
routed sign-paired family.

It is a divisor-level companion to g3_conjE_exact_halfset.py: instead of only
counting bad ratios, it prints the locator sparsity pattern that the proof
should force.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from itertools import combinations
from math import gcd, isqrt

from g3_conjE_exact_halfset import (
    orbit_representative,
    poly_mul_linear,
    rho_for_halfset,
    subgroup,
)


def poly_for_indices(L: list[int], indices: tuple[int, ...], q: int) -> list[int]:
    poly = [1]
    for i in indices:
        poly = poly_mul_linear(poly, L[i], q)
    return poly


def support(poly: list[int], q: int) -> tuple[int, ...]:
    return tuple(i for i, coeff in enumerate(poly[:-1]) if coeff % q)


def stabilizer(indices: tuple[int, ...], n: int) -> tuple[int, ...]:
    S = set(indices)
    return tuple(shift for shift in range(n) if {(i + shift) % n for i in S} == S)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument("--q", type=int, default=97)
    parser.add_argument("--a", type=int, required=True)
    parser.add_argument("--b", type=int, required=True)
    parser.add_argument("--max-show", type=int, default=30)
    args = parser.parse_args()

    k = args.k if args.k is not None else args.n // 4
    t = isqrt(k * args.n)
    if t * t != k * args.n:
        raise ValueError("sqrt(k*n) must be integral")
    L = subgroup(args.q, args.n)
    action_gen = pow(L[1], (args.a - args.b) % args.n, args.q)

    rows = []
    for indices in combinations(range(args.n), t):
        points = [L[i] for i in indices]
        kind, rho = rho_for_halfset(points, args.a, args.b, k, args.q)
        if kind != "one" or rho is None:
            continue
        P = poly_for_indices(L, indices, args.q)
        rows.append(
            {
                "indices": indices,
                "rho": rho,
                "nonzero": rho != 0,
                "support": support(P, args.q),
                "stabilizer": stabilizer(indices, args.n),
                "P": P,
            }
        )

    nonzero = [row for row in rows if row["nonzero"]]
    orbits = defaultdict(list)
    for row in nonzero:
        orbits[orbit_representative(row["rho"], args.q, action_gen)].append(row)
    support_counts = Counter(row["support"] for row in nonzero)
    stabilizer_counts = Counter(row["stabilizer"] for row in nonzero)
    print(
        f"locator divisor audit n={args.n} k={k} q={args.q} "
        f"(a,b)=({args.a},{args.b})"
    )
    print(
        f"certificates={len(rows)} nonzero={len(nonzero)} zero_boundary={len(rows)-len(nonzero)} "
        f"orbit_count={len(orbits)} orbit_size={args.n // gcd(abs(args.a-args.b), args.n)}"
    )
    print("support profiles:")
    for supp, count in support_counts.most_common():
        print(f"  support={supp} count={count}")
    print("stabilizer profiles:")
    for stab, count in stabilizer_counts.most_common():
        print(f"  stabilizer={stab} count={count}")
    for row in rows[: args.max_show]:
        boundary = "nonzero" if row["nonzero"] else "zero"
        print(
            f"  {boundary} rho={row['rho']} S={list(row['indices'])} "
            f"support={row['support']} stabilizer={row['stabilizer']} P={row['P']}"
        )


if __name__ == "__main__":
    main()
