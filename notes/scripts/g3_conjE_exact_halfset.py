"""Exact half-set certificate for Conjecture E.

For a 2-monomial pencil

    h_rho(z) = rho * z^a + z^b

on a cyclic domain L_n, the Johnson agreement threshold at rate 1/4 is
sqrt(k n) = n/2.  A ratio rho is bad iff there is a half-set S of L_n on
which h_rho agrees with a degree-<k polynomial.

For fixed S, interpolate h_rho on S.  The high interpolation coefficients
are linear in rho, so S contributes either no rho, one rho, or a degenerate
"all rho" certificate.  This script enumerates those exact certificates for
small n and groups the resulting bad ratios by the Theorem 0187 orbit action.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from itertools import combinations
from math import gcd, isqrt


def inv(x: int, q: int) -> int:
    return pow(x % q, q - 2, q)


def primitive_root(p: int) -> int:
    factors = []
    x = p - 1
    d = 2
    while d * d <= x:
        if x % d == 0:
            factors.append(d)
            while x % d == 0:
                x //= d
        d += 1
    if x > 1:
        factors.append(x)

    for g in range(2, p):
        if all(pow(g, (p - 1) // r, p) != 1 for r in factors):
            return g
    raise RuntimeError(f"no primitive root found for F_{p}")


def subgroup(q: int, n: int) -> list[int]:
    if (q - 1) % n != 0:
        raise ValueError(f"n={n} does not divide q-1={q-1}")
    w = pow(primitive_root(q), (q - 1) // n, q)
    return [pow(w, i, q) for i in range(n)]


def poly_mul_linear(poly: list[int], root: int, q: int) -> list[int]:
    out = [0] * (len(poly) + 1)
    for i, c in enumerate(poly):
        out[i] = (out[i] - c * root) % q
        out[i + 1] = (out[i + 1] + c) % q
    return out


def lagrange_basis_coeffs(points: list[int], q: int) -> list[list[int]]:
    """Return degree < len(points) Lagrange basis coefficients."""
    basis = []
    for i, xi in enumerate(points):
        poly = [1]
        denom = 1
        for j, xj in enumerate(points):
            if i == j:
                continue
            poly = poly_mul_linear(poly, xj, q)
            denom = denom * ((xi - xj) % q) % q
        scale = inv(denom, q)
        basis.append([(c * scale) % q for c in poly])
    return basis


def high_coeff_vector(points: list[int], exp: int, k: int, t: int, q: int) -> list[int]:
    basis = lagrange_basis_coeffs(points, q)
    coeff = [0] * t
    for z, bpoly in zip(points, basis):
        val = pow(z, exp, q)
        for i, c in enumerate(bpoly):
            coeff[i] = (coeff[i] + val * c) % q
    return coeff[k:t]


def rho_for_halfset(points: list[int], a: int, b: int, k: int, q: int) -> tuple[str, int | None]:
    t = len(points)
    avec = high_coeff_vector(points, a, k, t, q)
    bvec = high_coeff_vector(points, b, k, t, q)

    rho = None
    for A, B in zip(avec, bvec):
        if A == 0:
            if B != 0:
                return ("none", None)
            continue
        candidate = (-B * inv(A, q)) % q
        if rho is None:
            rho = candidate
        elif rho != candidate:
            return ("none", None)
    if rho is None:
        return ("all", None)
    return ("one", rho)


def orbit_representative(rho: int, q: int, action_gen: int) -> tuple[int, ...]:
    orbit = []
    x = rho
    while x not in orbit:
        orbit.append(x)
        x = x * action_gen % q
    return tuple(sorted(orbit))


def exact_bad_ratios(
    n: int,
    k: int,
    q: int,
    a: int,
    b: int,
    max_sets: int | None = None,
    keep_degenerate: int = 0,
    keep_ratio_witnesses: int = 0,
):
    t2 = k * n
    t = isqrt(t2)
    if t * t != t2:
        raise ValueError(f"sqrt(k*n) is not integral for n={n}, k={k}")

    L = subgroup(q, n)
    bad = defaultdict(int)
    zero_boundary = 0
    degenerate = 0
    degenerate_sets = []
    ratio_witnesses = defaultdict(list)
    checked = 0
    for indices in combinations(range(n), t):
        if max_sets is not None and checked >= max_sets:
            break
        checked += 1
        points = [L[i] for i in indices]
        kind, rho = rho_for_halfset(points, a, b, k, q)
        if kind == "all":
            degenerate += 1
            if len(degenerate_sets) < keep_degenerate:
                degenerate_sets.append(indices)
        elif kind == "one":
            if rho == 0:
                zero_boundary += 1
            else:
                bad[rho] += 1
                if len(ratio_witnesses[rho]) < keep_ratio_witnesses:
                    ratio_witnesses[rho].append(indices)

    w = L[1]
    action_gen = pow(w, (a - b) % n, q)
    orbits = defaultdict(list)
    for rho, mult in bad.items():
        orbits[orbit_representative(rho, q, action_gen)].append((rho, mult))

    return {
        "checked": checked,
        "threshold": t,
        "bad": dict(bad),
        "zero_boundary": zero_boundary,
        "degenerate": degenerate,
        "degenerate_sets": degenerate_sets,
        "orbits": dict(orbits),
        "ratio_witnesses": dict(ratio_witnesses),
        "orbit_size": n // gcd(abs(a - b), n),
        "L": L,
    }


def exponent_pair_sweep(n: int, k: int, q: int) -> list[dict[str, int]]:
    rows = []
    for a in range(k, n):
        for b in range(k, n):
            if a == b:
                continue
            result = exact_bad_ratios(n, k, q, a, b)
            rows.append(
                {
                    "a": a,
                    "b": b,
                    "orbit_size": result["orbit_size"],
                    "bad_nonzero": len(result["bad"]),
                    "orbit_count": len(result["orbits"]),
                    "zero_boundary": result["zero_boundary"],
                    "degenerate": result["degenerate"],
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument("--q", type=int, default=97)
    parser.add_argument("--a", type=int)
    parser.add_argument("--b", type=int)
    parser.add_argument("--max-sets", type=int, default=None)
    parser.add_argument("--show-degenerate", type=int, default=0)
    parser.add_argument("--show-ratio-witnesses", type=int, default=0)
    parser.add_argument("--show-coset-profile", action="store_true")
    parser.add_argument("--sweep", action="store_true")
    args = parser.parse_args()

    k = args.k if args.k is not None else args.n // 4
    if args.sweep:
        rows = exponent_pair_sweep(args.n, k, args.q)
        bad_rows = [r for r in rows if r["orbit_count"] > 1 or r["degenerate"] > 0]
        print(f"n={args.n} k={k} q={args.q} above-J ordered-pair sweep")
        print(f"checked_pairs={len(rows)}")
        print(f"max_orbit_count={max(r['orbit_count'] for r in rows)}")
        print(f"degenerate_pair_count={sum(1 for r in rows if r['degenerate'] > 0)}")
        print(f"zero_boundary_pair_count={sum(1 for r in rows if r['zero_boundary'] > 0)}")
        for r in bad_rows[:80]:
            print(
                "  "
                f"(a,b)=({r['a']},{r['b']}) orbit_size={r['orbit_size']} "
                f"bad_nonzero={r['bad_nonzero']} orbit_count={r['orbit_count']} "
                f"zero_boundary={r['zero_boundary']} degenerate={r['degenerate']}"
            )
        if len(bad_rows) > 80:
            print(f"  ... {len(bad_rows) - 80} more flagged rows")
        return

    if args.a is None or args.b is None:
        parser.error("--a and --b are required unless --sweep is passed")

    result = exact_bad_ratios(
        args.n,
        k,
        args.q,
        args.a,
        args.b,
        args.max_sets,
        args.show_degenerate,
        args.show_ratio_witnesses,
    )

    print(f"n={args.n} k={k} q={args.q} pencil=(rho*z^{args.a} + z^{args.b})")
    print(f"agreement threshold={result['threshold']} checked_halfsets={result['checked']}")
    print(f"bad_nonzero_ratio_count={len(result['bad'])} orbit_size={result['orbit_size']}")
    print(f"zero_boundary_halfsets={result['zero_boundary']}")
    print(f"degenerate_all-rho_halfsets={result['degenerate']}")
    for indices in result["degenerate_sets"]:
        points = [result["L"][i] for i in indices]
        print(f"  all-rho halfset indices={list(indices)}")
        print(f"  all-rho halfset points={points}")
    print(f"orbit_count={len(result['orbits'])}")
    for orbit, witnesses in sorted(result["orbits"].items(), key=lambda item: item[0]):
        loads = sum(mult for _, mult in witnesses)
        print(f"  orbit size={len(orbit):2d} loads={loads:4d} orbit={list(orbit)}")
        if args.show_ratio_witnesses:
            for rho, _ in sorted(witnesses):
                for indices in result["ratio_witnesses"].get(rho, []):
                    print(f"    rho={rho} halfset indices={list(indices)}")
                    if args.show_coset_profile:
                        profile = [sum(1 for i in indices if i % 4 == j) for j in range(4)]
                        print(f"      z^k-coset profile={profile} (mod-4 index classes)")


if __name__ == "__main__":
    main()
