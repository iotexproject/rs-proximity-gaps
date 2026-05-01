"""Probe the full Toeplitz block equation behind Note 0197.

For a half-set S with P_S(x)=prod_{s in S}(x-s), exact certification gives

    rho e_a + e_b = C(P_S) q_S

on the high coefficient window k..n-1.  For two certificates S,T and
rho_T = g rho_S, eliminating rho gives

    C(P_S) q_S - g^{-1} C(P_T) q_T = (1-g^{-1}) e_b.

This script checks, for concrete certificate pairs, the set of g for which
that full block equation is compatible.  This is stronger than the two-column
shadow in verify_N_g_kernel.py and is the object that should expose the
support-cancellation factor.
"""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
from math import gcd, isqrt

from g3_conjE_exact_halfset import (
    orbit_representative,
    poly_mul_linear,
    rho_for_halfset,
    subgroup,
)


def inv(x: int, q: int) -> int:
    return pow(x % q, q - 2, q)


def rank_mod_p(matrix: list[list[int]], q: int) -> int:
    rows = [[x % q for x in row] for row in matrix if any(x % q for x in row)]
    if not rows:
        return 0
    m = len(rows)
    n = len(rows[0])
    rank = 0
    for col in range(n):
        pivot = None
        for r in range(rank, m):
            if rows[r][col] % q:
                pivot = r
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = inv(rows[rank][col], q)
        rows[rank] = [(x * scale) % q for x in rows[rank]]
        for r in range(m):
            if r != rank and rows[r][col] % q:
                factor = rows[r][col] % q
                rows[r] = [(x - factor * y) % q for x, y in zip(rows[r], rows[rank])]
        rank += 1
        if rank == m:
            break
    return rank


def poly_for_indices(L: list[int], indices: tuple[int, ...], q: int) -> list[int]:
    poly = [1]
    for i in indices:
        poly = poly_mul_linear(poly, L[i], q)
    return poly


def toeplitz_high_matrix(P: list[int], k: int, n: int, t: int, q: int) -> list[list[int]]:
    rows = []
    for degree in range(k, n):
        row = []
        for j in range(t):
            idx = degree - j
            row.append(P[idx] % q if 0 <= idx < len(P) else 0)
        rows.append(row)
    return rows


def compatible_g_set(
    L: list[int],
    S: tuple[int, ...],
    T: tuple[int, ...],
    k: int,
    n: int,
    b: int,
    q: int,
) -> set[int]:
    t = len(S)
    C_S = toeplitz_high_matrix(poly_for_indices(L, S, q), k, n, t, q)
    C_T = toeplitz_high_matrix(poly_for_indices(L, T, q), k, n, t, q)
    out = set()
    for g in range(1, q):
        gin = inv(g, q)
        coeff = []
        aug = []
        for row_idx, (row_s, row_t) in enumerate(zip(C_S, C_T)):
            row = row_s + [(-gin * x) % q for x in row_t]
            rhs = (1 - gin) % q if row_idx == b - k else 0
            coeff.append(row)
            aug.append(row + [rhs])
        if rank_mod_p(coeff, q) == rank_mod_p(aug, q):
            out.add(g)
    return out


def exact_certificates(
    n: int,
    k: int,
    q: int,
    a: int,
    b: int,
    max_sets: int | None,
) -> list[dict[str, object]]:
    t2 = k * n
    t = isqrt(t2)
    if t * t != t2:
        raise ValueError(f"sqrt(k*n) is not integral for n={n}, k={k}")
    L = subgroup(q, n)
    certs = []
    checked = 0
    for indices in combinations(range(n), t):
        if max_sets is not None and checked >= max_sets:
            break
        checked += 1
        points = [L[i] for i in indices]
        kind, rho = rho_for_halfset(points, a, b, k, q)
        if kind == "one" and rho not in (None, 0):
            certs.append({"indices": indices, "rho": rho})
    return certs


def action_subgroup(n: int, q: int, a: int, b: int) -> set[int]:
    L = subgroup(q, n)
    gen = pow(L[1], (a - b) % n, q)
    out = set()
    x = 1
    while x not in out:
        out.add(x)
        x = x * gen % q
    return out


def fourth_roots(q: int) -> set[int]:
    return {x for x in range(1, q) if pow(x, 4, q) == 1}


def summarize_set(values: set[int], q: int, action_gen: int) -> str:
    if not values:
        return "[]"
    orbits = {}
    for value in values:
        orbits.setdefault(orbit_representative(value, q, action_gen), 0)
        orbits[orbit_representative(value, q, action_gen)] += 1
    reps = sorted(orbits, key=lambda item: item[0])
    return "; ".join(f"{list(orb)}" for orb in reps[:5])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument("--q", type=int, default=97)
    parser.add_argument("--a", type=int, required=True)
    parser.add_argument("--b", type=int, required=True)
    parser.add_argument("--max-sets", type=int, default=None)
    parser.add_argument("--max-cert-pairs", type=int, default=20)
    args = parser.parse_args()

    k = args.k if args.k is not None else args.n // 4
    L = subgroup(args.q, args.n)
    certs = exact_certificates(args.n, k, args.q, args.a, args.b, args.max_sets)
    action = action_subgroup(args.n, args.q, args.a, args.b)
    sign = fourth_roots(args.q) if abs(args.a - args.b) == args.n // 2 else set()
    allowed = action | sign
    action_gen = pow(L[1], (args.a - args.b) % args.n, args.q)

    print(
        f"Toeplitz N_g compatibility n={args.n} k={k} q={args.q} "
        f"(a,b)=({args.a},{args.b}) certs={len(certs)} "
        f"action_size={len(action)} sign_size={len(sign)}"
    )
    stats: Counter[str] = Counter()
    shown = 0
    checked = 0
    for i, cert_s in enumerate(certs):
        for cert_t in certs[i + 1 :]:
            if checked >= args.max_cert_pairs:
                break
            checked += 1
            true_g = cert_t["rho"] * inv(cert_s["rho"], args.q) % args.q
            compat = compatible_g_set(
                L,
                cert_s["indices"],
                cert_t["indices"],
                k,
                args.n,
                args.b,
                args.q,
            )
            forbidden = compat - allowed
            stats["pairs"] += 1
            stats["true_in_compat" if true_g in compat else "true_missing"] += 1
            stats["has_forbidden" if forbidden else "no_forbidden"] += 1
            stats[f"compat_size_{len(compat)}"] += 1
            if shown < 8:
                shown += 1
                print(
                    f"pair#{checked} rho=({cert_s['rho']},{cert_t['rho']}) true_g={true_g} "
                    f"compat_size={len(compat)} forbidden={sorted(forbidden)}"
                )
                print(f"  S={list(cert_s['indices'])} T={list(cert_t['indices'])}")
                print(f"  compat_orbits={summarize_set(compat, args.q, action_gen)}")
        if checked >= args.max_cert_pairs:
            break
    print(
        f"summary pairs={stats['pairs']} true_in_compat={stats['true_in_compat']} "
        f"true_missing={stats['true_missing']} no_forbidden={stats['no_forbidden']} "
        f"has_forbidden={stats['has_forbidden']}"
    )
    for key in sorted(k for k in stats if k.startswith("compat_size_")):
        print(f"  {key}={stats[key]}")


if __name__ == "__main__":
    main()
