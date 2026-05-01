"""g3_universal_closure_finder.py — find sparse closure pattern for any (a, b).

For each (a, b) at small scale, try various sparse σ_S templates and find
which one (if any) yields cert+div ⊆ I (i.e., substitute reduces to 0).

Templates tried (in order of sparsity):
1. σ_S = z^{2k} + p_k z^k + p_0 (2-coset, used in Notes 0203/0204)
2. σ_S = z^{2k} + p_{2k-1} z^{2k-1} + p_k z^k + p_1 z + p_0 (4-coset)
3. Other sparse templates based on codex's audit pattern.

Output: ρ-only polynomial implied by each template, with degree.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp
from itertools import combinations


def get_eqs_with_template(n, k, a, b, support):
    """Get cert + div eqs with σ_S supported only on `support` (subset of [0, 2k-1])."""
    x = sp.Symbol("x")
    rho = sp.Symbol("rho")
    t = n // 2

    # σ_S = z^{2k} + ∑_{i ∈ support} p_i z^i, p_i = 0 elsewhere.
    p_vars = [sp.Symbol(f"p{i}") for i in range(t)]
    P = x**t
    for i in support:
        P += p_vars[i] * x**i

    rem_a = sp.Poly(sp.rem(x**a, P, x), x)
    rem_b = sp.Poly(sp.rem(x**b, P, x), x)

    cert_eqs = [
        sp.expand(rho * rem_a.coeff_monomial(x**d) + rem_b.coeff_monomial(x**d))
        for d in range(k, t)
    ]
    div_eqs = [sp.expand(c) for c in sp.Poly(sp.rem(x**n - 1, P, x), x).all_coeffs()]

    return cert_eqs, div_eqs, p_vars, rho


def try_template(n, k, a, b, support):
    """Try σ_S template. Compute rho-only polynomial after eliminating support vars."""
    cert_eqs, div_eqs, p, rho = get_eqs_with_template(n, k, a, b, support)
    elim_vars = [p[i] for i in support]
    if not elim_vars:
        # σ_S = z^{2k}, all eqs are pure rho or constants
        all_eqs = cert_eqs + div_eqs
        return all_eqs

    try:
        # Use Sympy Groebner with lex order (eliminate p first, then rho)
        G = sp.groebner(cert_eqs + div_eqs, *elim_vars, rho, order="lex")
        rho_polys = []
        for poly in G.polys:
            expr = sp.factor(poly.as_expr())
            if not any(expr.has(v) for v in elim_vars) and expr != 0:
                rho_polys.append(expr)
        return rho_polys
    except Exception as e:
        return [f"ERROR: {e}"]


def find_smallest_closure(n, k, a, b, max_support_size=4, time_budget=30):
    """Try increasingly larger sparse supports until one closes."""
    t = n // 2
    print(f"\n=== finding closure for (n={n}, k={k}, a={a}, b={b}) ===")

    # Try minimal supports first
    for size in range(1, max_support_size + 1):
        for sup in combinations(range(t), size):
            sup = tuple(sup)
            if 0 not in sup and size > 0:
                continue  # σ_S has constant term usually
            t0 = time.time()
            try:
                result = try_template(n, k, a, b, sup)
                dt = time.time() - t0
                if dt > time_budget:
                    print(f"  support={sup}: TIMEOUT ({dt:.0f}s)")
                    continue
                if isinstance(result, list) and result:
                    str_result = [str(r)[:60] for r in result]
                    print(f"  support={sup} ({dt:.1f}s): rho_polys={str_result}")
                else:
                    print(f"  support={sup}: empty (no rho-only poly)")
            except Exception as e:
                print(f"  support={sup}: error {e}")


def main():
    cases = [
        (16, 4, 4, 10),  # non-sign-paired, gcd=2, orbit_size=8
        (16, 4, 5, 11),  # non-sign-paired, gcd=2 (different a)
        (16, 4, 4, 9),   # non-sign-paired, gcd=1
        (16, 4, 5, 10),  # non-sign-paired, gcd=1
        (16, 4, 4, 11),  # non-sign-paired, gcd=1
        (16, 4, 4, 13),  # non-sign-paired, gcd=1
    ]
    for n, k, a, b in cases:
        find_smallest_closure(n, k, a, b, max_support_size=3, time_budget=15)


if __name__ == "__main__":
    main()
