"""g3_closure_signpaired_8-2.py — Groebner closure for sign-paired (8, 2, 2, 6).

Test if locator divisor + cert equations FORCE coset-rigid form
P(x) = x^4 + p_2 x^2 + p_0 (i.e., p_1 = p_3 = 0).

Smaller scale than (16,4); should run in seconds.
"""
import sympy as sp


def main():
    x = sp.Symbol("x")
    p = sp.symbols("p0:4")
    rho = sp.Symbol("rho")
    n, k = 8, 2
    a, b = 2, 6
    t = n // 2  # 4

    P = x**t + sum(p[i] * x**i for i in range(t))
    rem_a = sp.Poly(sp.rem(x**a, P, x), x)
    rem_b = sp.Poly(sp.rem(x**b, P, x), x)

    cert_eqs = []
    for d in range(k, t):
        eq = sp.expand(rho * rem_a.coeff_monomial(x**d) + rem_b.coeff_monomial(x**d))
        cert_eqs.append(eq)

    print(f"Certificate equations (deg {k}..{t-1}):")
    for d, eq in zip(range(k, t), cert_eqs):
        print(f"  deg {d}: {eq}")

    div_eqs = [sp.expand(c) for c in sp.Poly(sp.rem(x**n - 1, P, x), x).all_coeffs()]
    print(f"\n{len(div_eqs)} divisor equations:")
    for i, eq in enumerate(div_eqs):
        print(f"  div[{i}]: {sp.factor(eq)}")

    print("\nComputing Groebner basis (lex order)...")
    all_eqs = cert_eqs + div_eqs
    G = sp.groebner(all_eqs, *p, rho, order="lex")
    print(f"Basis has {len(G.polys)} polynomials:")
    for i, poly in enumerate(G.polys):
        expr = sp.factor(poly.as_expr())
        print(f"  G[{i}]: {expr}")

    print("\n=== Coset-rigidity check (p_1, p_3 should be in ideal) ===")
    for var in [p[1], p[3]]:
        red = sp.reduced(var, list(G.polys), *p, rho, order="lex")[1]
        in_ideal = (red == 0)
        print(f"  {var} ∈ ideal (forced 0)?  {in_ideal}    reduced -> {red}")

    # Also rho-only
    print("\nrho-only polynomials in basis:")
    for poly in G.polys:
        expr = sp.factor(poly.as_expr())
        if not any(expr.has(var) for var in p) and expr != 0:
            deg = sp.Poly(expr, rho).degree()
            print(f"  deg {deg}: {expr}")


if __name__ == "__main__":
    main()
