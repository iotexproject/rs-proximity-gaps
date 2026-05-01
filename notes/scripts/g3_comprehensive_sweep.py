"""g3_comprehensive_sweep.py — comprehensive Φ_{a,b} sweep at multiple scales.

For each (n, k) ∈ {(8,2), (16,4), (32,8), (64,16)} and each (a, b) with
a, b ∈ [k, n) and a < b:
- Compute gcd(b-a, n), orbit_size, sign-paired flag
- Try minimal sparse support based on gcd
- Output Φ_{a,b}(ρ) and # bad ρ

Build a comprehensive table to demonstrate the Φ pattern empirically.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp
from math import gcd


def get_eqs_with_support(n, k, a, b, support):
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


def compute_Phi(n, k, a, b, support, time_budget=30):
    cert_eqs, div_eqs, p, rho = get_eqs_with_support(n, k, a, b, support)
    elim_vars = [p[i] for i in support]
    if not elim_vars:
        all_eqs = cert_eqs + div_eqs
        rho_polys = [eq for eq in all_eqs if not any(eq.has(v) for v in p)]
        return rho_polys
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


def support_from_gcd(n, k, gcd_val):
    """Conjecture: support = multiples of n/(2·m) where m = orbit_size."""
    # Actually more carefully: from empirical
    # gcd = n/2 (sign-paired): support {0, k}
    # gcd = n/4: support {0, k}
    # gcd = n/8: support {0, k/2, k, 3k/2}
    # gcd = n/16: support {0, k/4, k/2, ..., 7k/4}
    if gcd_val >= n // 4:
        return (0, k)
    period = n // (2 * (n // gcd_val))  # rough
    if period == 0:
        period = 1
    return tuple(range(0, 2*k, period))


def main():
    cases = []
    for n, k in [(8, 2), (16, 4), (32, 8)]:
        for a in range(k, n):
            for b in range(a+1, n):
                cases.append((n, k, a, b))

    rows = []
    for n, k, a, b in cases:
        r = b - a
        g = gcd(r, n)
        m = n // g
        sign_paired = (r == n // 2)

        # Try {0, k} support first (covers many cases)
        sup1 = (0, k)
        polys1 = compute_Phi(n, k, a, b, sup1, time_budget=10)

        # Try gcd-based support
        sup2 = support_from_gcd(n, k, g)
        polys2 = compute_Phi(n, k, a, b, sup2, time_budget=10) if sup2 != sup1 else polys1

        # Take the one with more info
        rho = sp.Symbol("rho")
        def deg(polys):
            best = 0
            for p in polys:
                if isinstance(p, str):
                    continue
                try:
                    d = sp.Poly(p, rho).degree()
                    best = max(best, d)
                except:
                    pass
            return best

        d1 = deg(polys1)
        d2 = deg(polys2)
        if d2 > d1:
            best_polys, best_sup = polys2, sup2
        else:
            best_polys, best_sup = polys1, sup1

        max_deg = max(d1, d2, 0)
        # Strip rho factor
        nz_deg = max_deg
        for p in best_polys:
            if isinstance(p, str): continue
            try:
                test = p
                while sp.simplify(test.subs(rho, 0)) == 0:
                    test = sp.simplify(test / rho)
                    nz_deg -= 1
                break
            except:
                pass
        # Just compute nonzero deg as deg - rho_pow
        rows.append({
            "n": n, "k": k, "a": a, "b": b,
            "gcd": g, "m": m, "sign_paired": sign_paired,
            "sup": best_sup, "deg": max_deg, "nz_deg": nz_deg,
            "Phi": str(best_polys[0]) if best_polys else "?"
        })

    # Print table
    print(f"\n{'n':>3} {'k':>3} {'a':>3} {'b':>3} {'gcd':>4} {'m':>3} {'SP':>3} {'sup':<14} {'deg':>4} {'nz':>4} Phi")
    for r in rows:
        sp_flag = "SP" if r["sign_paired"] else "  "
        print(f"{r['n']:>3} {r['k']:>3} {r['a']:>3} {r['b']:>3} {r['gcd']:>4} {r['m']:>3} {sp_flag:>3} "
              f"{str(r['sup']):<14} {r['deg']:>4} {r['nz_deg']:>4} {r['Phi'][:60]}")

    # Summary
    print("\n=== Summary ===")
    from collections import Counter
    by_n = {}
    for r in rows:
        by_n.setdefault(r["n"], []).append(r)
    for n_val, rs in sorted(by_n.items()):
        print(f"\n(n={n_val}, k={rs[0]['k']}): {len(rs)} pairs")
        print(f"  Max nz_deg: {max(r['nz_deg'] for r in rs)} (corresponds to max bad ρ count)")
        sp_count = sum(1 for r in rs if r['sign_paired'])
        print(f"  Sign-paired pairs: {sp_count}")
        # By gcd
        for g_val in sorted(set(r['gcd'] for r in rs)):
            grs = [r for r in rs if r['gcd'] == g_val]
            nzs = sorted(set(r['nz_deg'] for r in grs))
            print(f"  gcd={g_val} (m={n_val//g_val}): {len(grs)} pairs, nz_deg in {nzs}")


if __name__ == "__main__":
    main()
