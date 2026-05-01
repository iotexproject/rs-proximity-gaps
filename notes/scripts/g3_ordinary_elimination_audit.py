"""Run rho-elimination only on ordinary ConjE route rows.

This combines the cached exact pair sweep with the direct/triangular
rho-elimination engines.  It avoids wasting Groebner time on empty,
zero-boundary, all-rho boundary, or sign-paired rows.
"""

from __future__ import annotations

import argparse

import sympy as sp

from g3_conjE_cached_pair_sweep import exact_pair_sweep, route
from g3_arising_pair_obstruction_sweep import arising_pairs
from triangular_ratio_elimination_sweep import run_with_timeout


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n0", type=int, required=True)
    parser.add_argument("--q", type=int, default=97)
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()

    n = args.n0 // 4
    k = n // 4
    pairs = arising_pairs(args.n0, args.n0 // 4)
    rows = exact_pair_sweep(n, k, args.q, pairs)
    ordinary = [(row["a"], row["b"]) for row in rows if route(row) == "ordinary"]
    print(f"ordinary elimination audit n0={args.n0} n={n} k={k} q={args.q} ordinary_pairs={len(ordinary)}")
    for a, b in ordinary:
        case = (n, k, a, b)
        result = None
        used_method = None
        for method in ("direct", "triangular"):
            result = run_with_timeout(method, case, args.timeout)
            if result is not None and result["rho_only"]:
                used_method = method
                break
        if result is None:
            print(f"  (a,b)=({a},{b}) TIMEOUT")
            continue
        if not result["rho_only"]:
            print(f"  (a,b)=({a},{b}) unresolved")
            continue
        expr = result["rho_only"][0]
        degree = sp.Poly(expr, sp.Symbol("rho")).degree()
        print(f"  (a,b)=({a},{b}) method={used_method} degree={degree}: {expr}")


if __name__ == "__main__":
    main()
