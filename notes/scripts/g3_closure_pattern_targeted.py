"""g3_closure_pattern_targeted.py — test gcd-based support patterns for closure.

For (a, b) with gcd(b-a, n) = g, conjecture σ_S support = multiples of g/2 or similar.

Empirically test specific support patterns suggested by codex's audits and my (8,2)/(16,4) data.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp
from math import gcd


def get_eqs_with_template(n, k, a, b, support):
    x = sp.Symbol("x")
    rho = sp.Symbol("rho")
    t = n // 2
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


def try_support(n, k, a, b, support):
    cert_eqs, div_eqs, p, rho = get_eqs_with_template(n, k, a, b, support)
    elim_vars = [p[i] for i in support]
    if not elim_vars:
        return None
    try:
        G = sp.groebner(cert_eqs + div_eqs, *elim_vars, rho, order="lex")
        rho_polys = []
        for poly in G.polys:
            expr = sp.factor(poly.as_expr())
            if not any(expr.has(v) for v in elim_vars) and expr != 0:
                rho_polys.append(expr)
        return rho_polys
    except Exception as e:
        return [f"ERROR: {e}"]


def main():
    n, k = 16, 4
    cases = [
        (4, 10),  # gcd=2
        (5, 11),  # gcd=2
        (6, 8),   # gcd=2
        (4, 9),   # gcd=1
        (4, 11),  # gcd=1
        (5, 6),   # gcd=1
    ]
    # Support patterns to try for each
    support_templates = {
        "even": (0, 2, 4, 6),  # multiples of 2
        "{0,k}": (0, 4),        # 2-coset
        "all": tuple(range(8)),  # full
        "odd_skip": (0, 2, 4),
        "small_3": (0, 1, 3),  # codex (8,2,4,3) pattern
        "all_but_5_7": (0, 1, 2, 3, 4, 6),
    }

    for a, b in cases:
        g = gcd(b - a, n)
        orbit_size = n // g
        sign_paired = (b - a) % n == n // 2
        print(f"\n=== ({a}, {b}): gcd={g}, orbit_size={orbit_size}, sign-paired={sign_paired} ===")
        for name, sup in support_templates.items():
            t0 = time.time()
            try:
                result = try_support(n, k, a, b, sup)
                dt = time.time() - t0
                if dt > 30:
                    print(f"  {name}={sup} ({dt:.0f}s, slow): TIMEOUT-ish")
                    continue
                if result:
                    str_result = [str(r)[:80] for r in result]
                    print(f"  {name}={sup} ({dt:.1f}s): {str_result}")
                else:
                    print(f"  {name}={sup}: empty")
            except Exception as e:
                print(f"  {name}={sup}: error {e}")


if __name__ == "__main__":
    main()
