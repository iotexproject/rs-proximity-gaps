"""g3_substitute_verify_general.py — substitute verify with arbitrary support pattern.

For each (n, k, a, b) and chosen support, derive substitution rules from
cert eqs (express p_{higher} in terms of p_{base}), then substitute into divisor
eqs and check what ρ-only polynomial remains.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp


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


def analyze(n, k, a, b, support):
    """Compute Phi via Groebner with given support."""
    print(f"\n=== ({n}, {k}, {a}, {b}) support={support} ===")
    cert_eqs, div_eqs, p_vars, rho = get_eqs_with_support(n, k, a, b, support)
    elim_vars = [p_vars[i] for i in support]

    print(f"Cert eqs ({len(cert_eqs)} polynomials, deg up to {(n-1)*2}):")
    for d, eq in zip(range(k, n//2), cert_eqs):
        s = str(eq)
        if len(s) > 100: s = s[:100] + "..."
        print(f"  deg {d}: {s}")
    print(f"Div eqs ({len(div_eqs)}):")
    for i, eq in enumerate(div_eqs):
        s = str(eq)
        if len(s) > 100: s = s[:100] + "..."
        print(f"  div[{i}]: {s}")

    print(f"\nGroebner basis (lex order, eliminating {elim_vars}, then rho):")
    t0 = time.time()
    G = sp.groebner(cert_eqs + div_eqs, *elim_vars, rho, order="lex")
    print(f"  done in {time.time()-t0:.1f}s, basis size {len(G.polys)}")
    print(f"  Polynomials in basis:")
    for i, poly in enumerate(G.polys):
        expr = sp.factor(poly.as_expr())
        s = str(expr)
        if len(s) > 120: s = s[:120] + "..."
        print(f"    G[{i}]: {s}")

    print(f"\n  Rho-only polys in basis:")
    for poly in G.polys:
        expr = sp.factor(poly.as_expr())
        if not any(expr.has(v) for v in elim_vars) and expr != 0:
            print(f"    {expr}")


def main():
    cases = [
        # (n, k, a, b, support)
        (8, 2, 2, 6, (0, 2)),    # sign-paired, support {0, k}
        (16, 4, 4, 12, (0, 4)),  # sign-paired, support {0, k}
        (16, 4, 4, 8, (0, 4)),   # non-sign-paired (k, 2k)
        (16, 4, 4, 10, (0, 2, 4, 6)),  # non-sign-paired gcd=2
    ]
    for n, k, a, b, sup in cases:
        try:
            analyze(n, k, a, b, sup)
        except Exception as e:
            print(f"  EXCEPTION: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
